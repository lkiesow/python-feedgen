%define srcname feedgen

Name:           python-%{srcname}
Version:        0.2.5
Release:        1%{?dist}
Summary:        Feed Generator (ATOM, RSS, Podcasts)

Group:          Development/Libraries
License:        LGPLv3+ or BSD
URL:            http://lkiesow.github.io/%{name}/

Source0:        https://pypi.python.org/packages/source/f/%{srcname}/%{srcname}-%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
Requires:       python-lxml
Requires:       python-dateutil

%description
This module can be used to generate web feeds in both ATOM and RSS format. It
has support for extensions. Included is for example an extension to produce
Podcasts.


%prep
%setup -q -n %{srcname}-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
chmod 644 $RPM_BUILD_ROOT%{python_sitelib}/%{srcname}/*.py


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc docs/*
%{python_sitelib}/*


%changelog
* Mon Jul 22 2013 Lars Kiesow <lkiesow@uos.de> - 0.2.5-1
- Updated to 0.2.5-1

* Thu May 16 2013 Lars Kiesow <lkiesow@uos.de> - 0.2.4-1
- Update to 0.2.4

* Tue May 14 2013 Lars Kiesow <lkiesow@uos.de> - 0.2.3-1
- Update to 0.2.3

* Sun May  5 2013 Lars Kiesow <lkiesow@uos.de> - 0.2.2-1
- Update to version 0.2.2

* Sat May  4 2013 Lars Kiesow <lkiesow@uos.de> - 0.1-1
- Initial build
