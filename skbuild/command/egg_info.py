
import os

from setuptools.command.egg_info import egg_info as _egg_info
from setuptools.command.egg_info import manifest_maker as _manifest_maker


class egg_info(_egg_info):
    def finalize_options(self):
        if self.egg_base is not None:
            script_path = os.path.abspath(self.distribution.script_name)
            script_dir = os.path.dirname(script_path)
            self.egg_base = os.path.join(script_dir, self.egg_base)

        _egg_info.finalize_options(self)

    def find_sources(self):
        """Generate SOURCES.txt manifest file"""
        manifest_filename = os.path.join(self.egg_info, "SOURCES.txt")
        mm = manifest_maker(self.distribution)
        mm.manifest = manifest_filename
        mm.run()
        self.filelist = mm.filelist

class manifest_maker(_manifest_maker):

    def add_defaults(self):
        import ptpdb; ptpdb.set_trace()
        _manifest_maker.add_defaults(self)
        old_include_package_data = self.distribution.include_package_data
        # self.distribution.include_package_data = True
        build_py = self.get_finalized_command('build_py')
        df = build_py.data_files
        for _, src_dir, _, filenames in build_py.data_files:
            self.filelist.extend([os.path.join(src_dir, filename)
                                  for filename in filenames])
        self.distribution.include_package_data = old_include_package_data
