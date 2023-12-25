%global pypi_name feedgen
%global pypi_version 1.0.0

Name:           python-%{pypi_name}
Version:        %{pypi_version}
Release:        1%{?dist}
Summary:        Feed Generator (ATOM, RSS, Podcasts)

License:        BSD or LGPLv3
URL:            http://lkiesow.github.io/python-feedgen
#Source0:        https://github.com/lkiesow/%{name}/archive/v%{version}.tar.gz
Source0:        %{pypi_source}
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(lxml)
BuildRequires:  python3dist(python-dateutil)

%description
Feedgenerator: This module can be used to generate web feeds in both ATOM and
RSS format. It has support for extensions. Included is for example an extension
to produce Podcasts.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}

Requires:       python3dist(python-dateutil)
Requires:       python3dist(lxml)

%description -n python3-%{pypi_name}
Feedgenerator: This module can be used to generate web feeds in both ATOM and
RSS format. It has support for extensions. Included is for example an extension
to produce Podcasts.


%prep
%autosetup -n %{pypi_name}-%{pypi_version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%py3_build

%install
%py3_install

%check
%{__python3} setup.py test

%files -n python3-%{pypi_name}
%license license.lgpl license.bsd
%doc readme.rst
%{python3_sitelib}/%{pypi_name}
%{python3_sitelib}/%{pypi_name}-%{version}-py?.?.egg-info

%changelog
* Mon Dec 25 2023 Lars Kiesow <lkiesow@uos.de> - 1.0.0-1
- Update to 1.0.0
- Removing support for Python 2

* Sat May 19 2018 Lars Kiesow <lkiesow@uos.de> - 0.7.0-1
- Update to 0.7.0

* Tue Oct 24 2017 Lumir Balhar <lbalhar@redhat.com> - 0.6.1-1
- Initial package.
