%define srcname feedgen

Name:           python-%{srcname}
Version:        0.3.2
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
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires:       python-lxml
Requires:       python-dateutil

%description
This module can be used to generate web feeds in both ATOM and RSS format. It
has support for extensions. Included is for example an extension to produce
Podcasts.


%package -n python3-%{srcname}
Summary:        Feed Generator (ATOM, RSS, Podcasts)
Group:          Development/Libraries

Requires:       python3-lxml
Requires:       python3-dateutil

%description -n python3-%{srcname}
This module can be used to generate web feeds in both ATOM and RSS format. It
has support for extensions. Included is for example an extension to produce
Podcasts.


%prep
%setup -q -n %{srcname}-%{version}
mkdir python2
mv PKG-INFO  docs  feedgen  license.bsd  license.lgpl  readme.md  setup.py python2
cp -r python2 python3

# ensure the right python version is used
find python3 -name '*.py' | xargs sed -i '1s|^#!python|#!%{__python3}|'
find python2 -name '*.py' | xargs sed -i '1s|^#!python|#!%{__python2}|'


%build
pushd python2
%{__python2} setup.py build
popd
pushd python3
%{__python3} setup.py build
popd


%install
rm -rf $RPM_BUILD_ROOT
pushd python3
%{__python3} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
popd
pushd python2
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
popd
chmod 644 $RPM_BUILD_ROOT%{python3_sitelib}/%{srcname}/*.py
chmod 644 $RPM_BUILD_ROOT%{python2_sitelib}/%{srcname}/*.py


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%license python2/license.*
%doc python2/docs/*
%{python2_sitelib}/*


%files -n python3-%{srcname}
%defattr(-,root,root,-)
%license python3/license.*
%doc python3/docs/*
%{python3_sitelib}/*


%changelog
* Thu Oct 29 2015 Lars Kiesow <lkiesow@uos.de> 0.3.2-1
- Update to 0.3.2

* Mon May  4 2015 Lars Kiesow <lkiesow@uos.de> - 0.3.1-2
- Building for Python 3 as well

* Fri Jan 16 2015 Lars Kiesow <lkiesow@uos.de> - 0.3.1-1
- Update to 0.3.1

* Sun Jul 20 2014 Lars Kiesow <lkiesow@uos.de> - 0.3.0-1
- Update to 0.3

* Wed Jan  1 2014 Lars Kiesow <lkiesow@uos.de> - 0.2.8-1
- Update to 0.2.8


* Wed Jan  1 2014 Lars Kiesow <lkiesow@uos.de> - 0.2.7-1
- Update to 0.2.7

* Mon Sep 23 2013 Lars Kiesow <lkiesow@uos.de> - 0.2.6-1
- Update to 0.2.6

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
