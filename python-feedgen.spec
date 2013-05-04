# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%define srcname feedgen

Name:           python-%{srcname}
Version:        0.1
Release:        1%{?dist}
Summary:        Feed Generator (ATOM, RSS, Podcasts)

Group:          Development/Libraries
License:        LGPLv3+ or BSD
URL:            https://pypi.python.org/pypi/%{srcname}/

Source0:        https://pypi.python.org/packages/source/f/%{srcname}/%{srcname}-%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools
Requires:       python-lxml
Requires:       python-dateutil

%description
This module can be used to generate web feeds in both ATOM and RSS format. The
included PodcastGenerator can furthermore generate all of Apples RSS extension
for Podcasts.

%prep
%setup -q -n %{srcname}-%{version}
# remove shebang from library files
sed -i '/^\#\!.*python$/d' %{srcname}/*.py


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
* Sat May  4 2013 Lars Kiesow <lkiesow@uos.de> - 0.1-1
- Initial build
