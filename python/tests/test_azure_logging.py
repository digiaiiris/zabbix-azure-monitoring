import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

PYTHON_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_script(body, argv, log_dir):
    """Run a decorated main() in a fresh interpreter, like the Zabbix agent does."""
    code = "\n".join([
        "import sys",
        "from ic_azure import azure_logging",
        "",
        "@azure_logging.log_run('test_script')",
        "def main():",
        textwrap.indent(textwrap.dedent(body).strip(), "    "),
        "",
        "main()",
    ])
    env = dict(os.environ, AZURE_MONITORING_LOG_DIR=log_dir, PYTHONPATH=PYTHON_DIR)
    return subprocess.run(
        [sys.executable, "-c", code] + argv, env=env, capture_output=True, text=True
    )


def read_log(log_dir):
    with open(os.path.join(log_dir, "test_script.log")) as fh:
        return fh.read()


class TestAzureLogging(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log_dir = os.path.join(self.tmp.name, "logs")

    def tearDown(self):
        self.tmp.cleanup()

    def test_success_logs_context_and_output_size_without_touching_stdout(self):
        result = run_script(
            """
            azure_logging.set_resource(
                "/subscriptions/sub-1/resourceGroups/RG-PROD/providers/"
                "Microsoft.Sql/servers/sql-01/databases/hw")
            azure_logging.emit('{"data": [1, 2]}', items=2)
            """,
            ["customer/customer-azure-config.json", "res"], self.log_dir
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '{"data": [1, 2]}\n')
        self.assertEqual(result.stderr, "")
        log = read_log(self.log_dir)
        self.assertIn("config=customer/customer-azure-config.json", log)
        self.assertIn("sub=sub-1 rg=RG-PROD resource=servers/sql-01/databases/hw", log)
        self.assertIn("Started", log)
        self.assertIn("OK (", log)
        self.assertIn("bytes=16 items=2", log)

    def test_sys_exit_error_is_logged_and_still_reaches_zabbix(self):
        result = run_script(
            'sys.exit("Client request failed. boom")', ["cfg.json"], self.log_dir
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "Client request failed. boom\n")
        log = read_log(self.log_dir)
        self.assertIn("ERROR", log)
        self.assertIn("Client request failed. boom", log)

    def test_exception_traceback_is_logged(self):
        result = run_script('raise ValueError("bad timegrain")', ["cfg.json"], self.log_dir)
        self.assertNotEqual(result.returncode, 0)
        log = read_log(self.log_dir)
        self.assertIn("Traceback", log)
        self.assertIn("ValueError: bad timegrain", log)

    def test_output_over_zabbix_limit_is_warned(self):
        run_script(
            "azure_logging.emit('x' * (512 * 1024 + 1), items=9)", ["cfg.json"], self.log_dir
        )
        self.assertIn("exceeding Zabbix agent limit", read_log(self.log_dir))

    def test_unwritable_log_dir_does_not_change_item_output(self):
        blocker = os.path.join(self.tmp.name, "file")
        open(blocker, "w").close()
        result = run_script(
            'azure_logging.emit("42")', ["cfg.json"], os.path.join(blocker, "logs")
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "42\n")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
