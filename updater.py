import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpn
import json
import os
import traceback


class Updater(kp.Plugin):
    GITHUB_API_URL = "https://api.github.com/repos/Keypirinha/Keypirinha/releases"
    UPDATE_COMMAND_CAT = kp.ItemCategory.USER_BASE + 1
    UPDATE_COMMAND = "update"
    NO_NAG_ACTION = "no_nag"
    UPDATE_ACTION = "do_update"
    DEFAULT_KIND = "full"

    def __init__(self):
        super().__init__()
        self._url_opener = kpn.build_urllib_opener()
        self._newest_version = kp.version()
        self._newest_release = None
        self._no_nag = False
        self._kind = self.DEFAULT_KIND

    def on_start(self):
        self._read_config()

        self._cleanup()

        self.set_actions(self.UPDATE_COMMAND_CAT, [
            self.create_action(
                name=self.NO_NAG_ACTION,
                label="Stop nagging me!",
                short_desc="Stops suggesting to update as very first item in the results list"
            ),
            self.create_action(
                name=self.UPDATE_ACTION,
                label="Do the update",
                short_desc="Update keypirinha to the newest version"
            )
        ])

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self._read_config()
            self.on_catalog()

        if flags & kp.Events.NETOPTIONS:
            self._url_opener = kpn.build_urllib_opener()

    def on_catalog(self):
        self._newest_version = self._get_newest_version()
        if self.compare_version(self._newest_version, kp.version()):
            self.info("There is a new version:", ".".join(str(n) for n in self._newest_version))
            if self._no_nag:
                items = [self.create_item(
                    category=self.UPDATE_COMMAND_CAT,
                    label="Update Keypirinha to " + ".".join(str(n) for n in self._newest_version),
                    short_desc="Perform the update to the new version. A restart of keypirinha will occur.",
                    target=self.UPDATE_COMMAND,
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.IGNORE
                )]
                self.set_catalog(items)
        else:
            self.info(kp.name(), "is up to date.")

    def on_suggest(self, user_input, items_chain):
        if self.compare_version(self._newest_version, kp.version()) and not self._no_nag:
            items = [self.create_item(
                category=self.UPDATE_COMMAND_CAT,
                label="Update Keypirinha to " + ".".join(str(n) for n in self._newest_version),
                short_desc="Perform the update to the new version. A restart of keypirinha will occur.",
                target=self.UPDATE_COMMAND,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE
            )]
            self.set_suggestions(items, kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, action):
        if item.target() == self.UPDATE_COMMAND:
            if action and action.name() == self.NO_NAG_ACTION:
                self._no_nag = True
                self.on_catalog()
                return
            if self._newest_release is not None:
                for asset in self._newest_release["assets"]:
                    if self._kind in asset["name"]:
                        self._do_update(asset["browser_download_url"])
                        break

    def _read_config(self):
        self.dbg("Reading config")
        settings = self.load_settings()

        self._debug = settings.get_bool("debug", "main", False)

        self._kind = settings.get_enum(
            "kind",
            "main",
            self.DEFAULT_KIND,
            ["x86", "x64", "full"]
        )
        self.dbg("kind =", self._kind)

    @staticmethod
    def _make_tuple(version_str):
        return tuple(int(n) for n in version_str.lstrip("v").split("."))

    def _get_newest_version(self):
        self._newest_release = self._get_newest_release()
        return self._make_tuple(self._newest_release["tag_name"])

    def _get_newest_release(self):
        with self._url_opener.open(self.GITHUB_API_URL) as resp:
            releases = json.loads(resp.read().decode())

        max_version = (0, 0)
        max_release = None
        for release in releases:
            release_version = self._make_tuple(release["tag_name"])
            if self.compare_version(release_version, max_version) > 0:
                max_version = release_version
                max_release = release
        return max_release

    @staticmethod
    def compare_version(left, right):
        idx = 0
        while idx < len(left) and idx < len(right):
            if left[idx] != right[idx]:
                if left[idx] > right[idx]:
                    return 1
                else:
                    return -1
            idx += 1
        if idx < len(left) and left[idx] == 0:
            return 0
        if idx < len(right) and right[idx] == 0:
            return 0
        return 0

    def _do_update(self, download_url):
        self.dbg("Doing update")
        src_7z = self._download(download_url)

        self.dbg("Extracting update scripts to keypirinha cache")
        cmd_file = os.path.join(self.get_package_cache_path(), "update.cmd")
        with open(cmd_file, "wb") as cmd:
            cmd.write(self.load_binary_resource("update.cmd".format(self.package_full_name())))
        ps1_file = os.path.join(self.get_package_cache_path(), "updater.ps1")
        with open(ps1_file, "wb") as ps1:
            ps1.write(self.load_binary_resource("updater.ps1".format(self.package_full_name())))
        dest_dir = self._get_install_dir()
        args = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps1_file, '"{}"'.format(src_7z), '"{}"'.format(dest_dir)]
        if not self._can_read_write(dest_dir):
            args.append("-admin")
        self.dbg("Calling update script:", args)
        kpu.shell_execute("powershell", args, show=0)

    def _download(self, download_url):
        self.info("Downloading new keypirinha from:", download_url)
        out_path = os.path.join(self.get_package_cache_path(True), "kp.7z")

        if not os.path.exists(out_path):
            with self._url_opener.open(download_url) as resp, \
                    open(out_path, "wb") as kp_archive:
                length = resp.info().get("Content-Length")
                read = 0
                if length is not None:
                    length = int(length)
                    dl_out = "{:0.1f}".format(100 * read / length)
                else:
                    dl_out = "."
                chunk_size = 65536
                for chunk in iter(lambda: resp.read(chunk_size), ""):
                    if length is not None:
                        read += chunk_size
                        dl_out = "{:0.1f}%".format(100 * read / length)
                    else:
                        dl_out += "."
                    self.info(dl_out)
                    if not chunk:
                        break
                    kp_archive.write(chunk)
        self.info("Downloaded.")
        return out_path

    def _get_install_dir(self):
        install_dir = os.path.dirname(kp.exe_path())
        self.dbg("Install dir:", install_dir)
        return install_dir

    def _can_read_write(self, path):
        try:
            test_path = os.path.join(path, "test.txt")
            with open(test_path, "w") as test:
                test.write("test")
            with open(test_path, "r") as test:
                test.read()
            os.remove(test_path)
            return True
        except PermissionError:
            self.dbg(traceback.format_exc())
            return False

    def _cleanup(self):
        top = self.get_package_cache_path()
        self.dbg("Cleaning up:", top)
        try:
            for root, dirs, files in os.walk(top, topdown=False):
                for name in files:
                    path = os.path.join(root, name)
                    self.dbg("Removing file:", path)
                    os.remove(path)
                for name in dirs:
                    path = os.path.join(root, name)
                    self.dbg("Removing dir:", path)
                    os.rmdir(path)
        except:
            self.err(traceback.format_exc())
