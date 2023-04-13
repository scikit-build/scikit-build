%global pypi_name scikit_build

Name:           python-scikit-build
Version:        0.0.0
Release:        %{autorelease}
Summary:        Improved build system generator for Python C/C++/Fortran/Cython extensions

# This project is mainly MIT but LICENSE also mentions some code
# that is BSD-2-Clause-Views licensed.
# All bundled(cmake()) files listed are Apache-2.0 licensed.
License:        MIT AND BSD-2-Clause-Views AND Apache-2.0
URL:            https://github.com/scikit-build/scikit-build
Source0:        %{pypi_source %{pypi_name}}
Source1:        %{name}.rpmlintrc

BuildArch:      noarch
BuildRequires:  python3-devel

# For tests:
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  git-core
BuildRequires:  ninja-build

%global _description %{expand:
Improved build system generator for CPython C/C++/Fortran/Cython extensions.
Better support is available for additional compilers, build systems,
cross compilation, and locating dependencies
and determining their build requirements.
The scikit-build package is fundamentally just glue between
the setuptools Python module and CMake.
}

%description %_description

%package -n python3-scikit-build
Summary:        %{summary}
Requires:       cmake
Requires:       ninja-build

# Files listed below are located in skbuild/resources/cmake.
# Since they contain "Copyright 2011 Kitware, Inc." in them we list them as bundled,
# their versions are unknown.
# There is no such copyright in the remaining files so we assume
# they are original part of the project.
Provides:       bundled(cmake(FindCython))
Provides:       bundled(cmake(FindPythonExtensions))
Provides:       bundled(cmake(UseCython))
Provides:       bundled(cmake(UseF2PY))
Provides:       bundled(cmake(UsePythonExtensions))

%description -n python3-scikit-build %_description


%prep
%autosetup -n %{pypi_name}-%{version}


%generate_buildrequires
%pyproject_buildrequires -x test


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files skbuild


%check
# Some tests have assumptions that don't work if the RPM build flags are set,
# so we clean them.
export CFLAGS=' '
export CXXFLAGS=' '
# pep518 tests are disabled because they require internet
%pytest -k "not pep518" \
        -m "not deprecated and not nosetuptoolsscm"


%files -n python3-scikit-build -f %{pyproject_files}
%doc README.*


%changelog
%autochangelog
