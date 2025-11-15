import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _install_requests_stub():
    requests_module = types.ModuleType("requests")

    class DummySession:
        def request(self, *args, **kwargs):  # pragma: no cover - never called
            raise RuntimeError("Dummy session should be overridden in tests")

    requests_module.Session = DummySession
    sys.modules.setdefault("requests", requests_module)


def _install_google_api_stubs():
    googleapiclient = types.ModuleType("googleapiclient")
    discovery = types.ModuleType("googleapiclient.discovery")

    def build(*args, **kwargs):  # pragma: no cover
        raise RuntimeError("build should be patched in tests")

    discovery.build = build

    errors = types.ModuleType("googleapiclient.errors")

    class HttpError(Exception):
        pass

    errors.HttpError = HttpError

    sys.modules.setdefault("googleapiclient", googleapiclient)
    sys.modules.setdefault("googleapiclient.discovery", discovery)
    sys.modules.setdefault("googleapiclient.errors", errors)

    oauth2 = types.ModuleType("google.oauth2")
    service_account = types.ModuleType("google.oauth2.service_account")

    class Credentials:
        @classmethod
        def from_service_account_file(cls, path, scopes=None):  # pragma: no cover
            return cls()

    service_account.Credentials = Credentials
    sys.modules.setdefault("google.oauth2", oauth2)
    sys.modules.setdefault("google.oauth2.service_account", service_account)


_install_requests_stub()
_install_google_api_stubs()
