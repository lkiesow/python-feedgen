%global pypi_name feedgen

Name:           python-%{pypi_name}
Version:        0.9.0
Release:        1%{?dist}
Summary:        Feed Generator (ATOM, RSS, Podcasts)

License:        BSD or LGPLv3
URL:            http://lkiesow.github.io/python-feedgen
Source0:        https://github.com/lkiesow/%{name}/archive/v%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python2-dateutil
BuildRequires:  python2-devel
BuildRequires:  python2-lxml
BuildRequires:  python2-setuptools

BuildRequires:  python3-dateutil
BuildRequires:  python3-devel
BuildRequires:  python3-lxml
BuildRequires:  python3-setuptools

%description
Feedgenerator This module can be used to generate web feeds in both ATOM and
RSS format. It has support for extensions. Included is for example an extension
to produce Podcasts.

%package -n     python2-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python2-%{pypi_name}}

Requires:       python2-dateutil
Requires:       python2-lxml
%description -n python2-%{pypi_name}
Feedgenerator This module can be used to generate web feeds in both ATOM and
RSS format. It has support for extensions. Included is for example an extension
to produce Podcasts.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}

Requires:       python3-dateutil
Requires:       python3-lxml
%description -n python3-%{pypi_name}
Feedgenerator This module can be used to generate web feeds in both ATOM and
RSS format. It has support for extensions. Included is for example an extension
to produce Podcasts.


%prep
%autosetup
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%py2_build
%py3_build

%install
%py2_install
%py3_install


%check
%{__python2} setup.py test
%{__python3} setup.py test

%files -n python2-%{pypi_name}
%license license.lgpl license.bsd
%doc readme.rst
%{python2_sitelib}/%{pypi_name}
%{python2_sitelib}/%{pypi_name}-%{version}-py?.?.egg-info

%files -n python3-%{pypi_name}
%license license.lgpl license.bsd
%doc readme.rst
%{python3_sitelib}/%{pypi_name}
%{python3_sitelib}/%{pypi_name}-%{version}-py?.?.egg-info

%changelog
* Sat May 19 2018 Lars Kiesow <lkiesow@uos.de> - 0.7.0-1
- Update to 0.7.0

* Tue Oct 24 2017 Lumir Balhar <lbalhar@redhat.com> - 0.6.1-1
- Initial package.
