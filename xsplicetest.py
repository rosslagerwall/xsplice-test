import subprocess
import os
import os.path
import shutil
import re
import random

class Patch:
    def __init__(self, name, options):
        self.name = name
        self.buildid = None
        self.path = "patches/%s.patch" % name
        self.outdir = "out-%s" % name
        self.binpath = os.path.join(self.outdir, "%s.xsplice" % name)
        options = options.split(',')
        self.ignore = 'ignore' in options
        self.reverse = 'reverse' in options

class _Testcase:
    def __init__(self, host, patches):
        self.host = host
        self.patches = patches

        lines = self.runcmd_out("xl info")
        for line in lines:
            if line.startswith("build_id "):
                self.xen_buildid = line.split(":")[1].strip()

    def _build(self, patch):
        shutil.rmtree(patch.outdir, ignore_errors=True)
        args = ['../xsplice-build/xsplice-build',
                '--xen-debug',
                #'--xen-syms', '../xen-syms',
                '-s', '../src',
                '-p', patch.path,
                '-o', patch.outdir]
        subprocess.check_call(args)

        args = ['readelf', '-Wn',
                patch.binpath]
        lines = subprocess.check_output(args, universal_newlines=True)
        for line in lines.split("\n"):
            if "Build ID:" in line:
                patch.buildid = line.split()[2]
        print(patch.buildid)

        with open(patch.path, "r") as f:
            subprocess.check_call(['patch', '-f', '-p1'],
                                  stdin=f,
                                  cwd='../src')

        args = ['scp', patch.binpath, self.host + ":"]
        subprocess.check_call(args)

    def build(self):
        print("===== BUILD =====")

        for patch in self.patches:
            if patch.reverse:
                with open(patch.path, "r") as f:
                    subprocess.check_call(['patch', '-f', '-R', '-p1'],
                                          stdin=f,
                                          cwd='../src')
            elif not patch.ignore:
                self._build(patch)

    def run(self):
        print("===== RUN =====")

        patches = self.do_list()
        if len(patches) > 0:
            raise Exception("Host has patches loaded")

    def _runcmd(self, cmd):
        args = ['ssh', self.host, "%s" % cmd]
        return subprocess.check_call(args)

    def runcmd(self, cmd):
        print("Running command: " + cmd)
        return self._runcmd(cmd)

    def cleanup(self):
        print("===== CLEANUP =====")

        # Unload patches
        changed = True
        while changed:
            changed = False
            patches = self.do_list()
            for patch in patches:
                if patches[patch][0] == 'APPLIED':
                    try:
                        self.do_revert(patch)
                        changed = True
                    except subprocess.CalledProcessError as e:
                        pass

                try:
                    self.do_unload(patch)
                    changed = True
                except subprocess.CalledProcessError as e:
                    pass

        # Unpatch the source tree
        for patch in reversed(self.patches):
            with open(patch.path, "r") as f:
                args = ['patch', '-p1']
                if not patch.reverse:
                    args.append('-R')
                subprocess.check_call(args, stdin=f, cwd='../src')

    def runcmd_out(self, cmd):
        args = ['ssh', self.host, "%s" % cmd]
        return subprocess.check_output(args, universal_newlines=True)

    def record_log(self):
        lines = self.runcmd_out("xl dmesg")
        lines = [line.strip() for line in lines.split("\n") if line.strip()]
        self._mark = lines[-1].strip()

    def grep_log(self, s, record=True):
        marked = False
        lines = self.runcmd_out("xl dmesg")
        lines = [line.strip() for line in lines.split("\n") if line.strip()]

        for line in lines:
            if line == self._mark:
                marked = True
                continue
            if not marked:
                continue

            if re.search(s, line):
                if record:
                    self._mark = line
                return s

        if record:
            self._mark = lines[-1]
        return None

    def assert_log(self, s, record=True):
        assert self.grep_log(s, record)

    def assert_not_log(self, s, record=True):
        assert self.grep_log(s, record) is None

    def do_list(self):
        patches = {}

        out = self.runcmd_out("xen-xsplice list")
        for line in out.split("\n")[2:]:
            line = line.strip()
            if not line:
                continue
            line = line.split("|", 1)
            status = line[1].strip()
            m = re.match(r"(.+) \((\d+), .*\)$", status)
            if m:
                status = (m.group(1), int(m.group(2)))
            else:
                status = (status, 0)
            patches[line[0].strip()] = status

        return patches

    def get_status(self, patch):
        patches = self.do_list()
        return patches.get(patch, ('ENOENT', 0))

    def load(self, patch):
        if random.randint(0, 1):
            self.do_load(patch)
        else:
            self.do_upload(patch)
            self.do_check(patch)
            self.do_apply(patch)
            assert self.get_status(patch)[0] == 'APPLIED'

    def do_load(self, patch):
        self.runcmd("xen-xsplice load %s.xsplice" % patch)
        assert self.get_status(patch)[0] == 'APPLIED'

    def do_upload(self, patch):
        self.runcmd("xen-xsplice upload %s %s.xsplice" % (patch, patch))
        assert self.get_status(patch)[0] == 'LOADED'

    def do_check(self, patch):
        self.runcmd("xen-xsplice check %s" % patch)
        assert self.get_status(patch)[0] == 'CHECKED'

    def do_apply(self, patch):
        self.runcmd("xen-xsplice apply %s" % patch)
        assert self.get_status(patch)[0] == 'APPLIED'

    def do_replace(self, patch):
        self.runcmd("xen-xsplice replace %s" % patch)

        patches = self.do_list()
        for p in patches:
            if p == patch:
                assert patches[p][0] == 'APPLIED'
            else:
                assert patches[p][0] == 'CHECKED' or \
                       patches[p][0] == 'LOADED'

    def do_revert(self, patch):
        self.runcmd("xen-xsplice revert %s" % patch)
        assert self.get_status(patch)[0] == 'CHECKED'

    def do_unload(self, patch):
        self.runcmd("xen-xsplice unload %s" % patch)
        assert self.get_status(patch)[0] == 'ENOENT'
