%if 0%{?fedora}
%global with_python3 1
%endif

Name:           custodia
Version:        0.2.dev1
Release:        1%{?dist}
Summary:        A service to manage, retrieve and store secrets for other processes.

License:        GPLv3+
URL:            https://github.com/latchset/%{name}
Source0:        https://github.com/latchset/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.gz
# Source1:        https://github.com/latchset/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.gz.sha512sum.txt

BuildArch:      noarch

BuildRequires:      python2-devel
BuildRequires:      python-jwcrypto
BuildRequires:      python2-requests
BuildRequires:      python2-setuptools >= 18
BuildRequires:      python2-coverage
BuildRequires:      python-tox >= 2.3.1
BuildRequires:      python2-pytest
BuildRequires:      python2-python-etcd
BuildRequires:      python-docutils

%if 0%{?with_python3}
BuildRequires:      python3-devel
BuildRequires:      python3-jwcrypto
BuildRequires:      python3-requests
BuildRequires:      python3-setuptools > 18
BuildRequires:      python3-coverage
BuildRequires:      python3-pytest
BuildRequires:      python3-python-etcd
BuildRequires:      python3-docutils
%endif

Requires:           python2-custodia = %{version}-%{release}

%description
A service to manage, retrieve and store secrets for other processes.


%package -n python2-custodia
Summary:    Subpackage with python2 custodia modules
Provides:   python-custodia
Obsoletes:  python-custodia <= 0.1.0
Requires:   python2-configparser
Requires:   python-jwcrypto
Requires:   python2-requests
Requires:   python2-setuptools

%description -n python2-custodia
Subpackage with python custodia modules


%package -n python2-custodia-extra
Summary:    Subpackage with python2 custodia extra modules
Requires:   python2-python-etcd
Requires:   python2-custodia = %{version}-%{release}

%description -n python2-custodia-extra
Subpackage with python2 custodia extra modules (etcdstore)


%if 0%{?with_python3}
%package -n python3-custodia
Summary:    Subpackage with python3 custodia modules
Requires:   python3-jwcrypto
Requires:   python3-requests
Requires:   python3-setuptools

%description -n python3-custodia
Subpackage with python custodia modules

%package -n python3-custodia-extra
Summary:    Subpackage with python3 custodia extra modules
Requires:   python3-python-etcd
Requires:   python3-custodia = %{version}-%{release}

%description -n python3-custodia-extra
Subpackage with python3 custodia extra modules (etcdstore)
%endif


%prep
# grep `sha512sum %{SOURCE0}` %{SOURCE1} || (echo "Checksum invalid!" && exit 1)
%autosetup


%build
%{__python2} setup.py egg_info build
%if 0%{?with_python3}
%{__python3} setup.py egg_info build
%endif


%check
# don't download packages
export PIP_INDEX_URL=http://host.invalid./
tox -e py27 -- --skip-servertests
%if 0%{?with_python3}
tox -e py35 -- --skip-servertests
%endif


%install
mkdir -p %{buildroot}/%{_sbindir}
mkdir -p %{buildroot}/%{_mandir}/man7
mkdir -p %{buildroot}/%{_defaultdocdir}/custodia
mkdir -p %{buildroot}/%{_defaultdocdir}/custodia/examples
mkdir -p %{buildroot}/%{_sysconfdir}/custodia
mkdir -p %{buildroot}/%{_unitdir}
mkdir -p %{buildroot}/%{_localstatedir}/lib/custodia
mkdir -p %{buildroot}/%{_localstatedir}/log/custodia
mkdir -p %{buildroot}/%{_localstatedir}/run/custodia

%{__python2} setup.py install --skip-build --root %{buildroot}
mv %{buildroot}/%{_bindir}/custodia %{buildroot}/%{_sbindir}/custodia
mv %{buildroot}/%{_bindir}/custodia-cli %{buildroot}/%{_bindir}/custodia-cli-2
install -t "%{buildroot}/%{_mandir}/man7" man/custodia.7
install -t "%{buildroot}/%{_defaultdocdir}/custodia" README API.md
install -t "%{buildroot}/%{_defaultdocdir}/custodia/examples" custodia.conf
install -t "%{buildroot}/%{_sysconfdir}/custodia" contrib/systemd/custodia.conf
install -t "%{buildroot}/%{_unitdir}" contrib/systemd/custodia.socket contrib/systemd/custodia.service

%if 0%{?with_python3}
%{__python3} setup.py install --skip-build --root %{buildroot}
rm %{buildroot}/%{_bindir}/custodia
mv %{buildroot}/%{_bindir}/custodia-cli-2 %{buildroot}/%{_bindir}/custodia-cli
%endif


%files
%doc README API.md
%doc %{_defaultdocdir}/custodia/examples/custodia.conf
%license LICENSE
%{_mandir}/man7/custodia*
%{_sbindir}/custodia
%{_bindir}/custodia-cli
%dir %attr(0700,root,root) %{_sysconfdir}/custodia
%config(noreplace) %attr(600,root,root) %{_sysconfdir}/custodia/custodia.conf
%attr(644,root,root)  %{_unitdir}/custodia.socket
%attr(644,root,root)  %{_unitdir}/custodia.service
%dir %attr(0700,root,root) %{_localstatedir}/lib/custodia
%dir %attr(0700,root,root) %{_localstatedir}/log/custodia
%dir %attr(0755,root,root) %{_localstatedir}/run/custodia

%files -n python2-custodia
%license LICENSE
%exclude %{python2_sitelib}/custodia/store/etcdstore.py*
%{python2_sitelib}/*

%files -n python2-custodia-extra
%license LICENSE
%{python2_sitelib}/custodia/store/etcdstore.py*

%if 0%{?with_python3}
%files -n python3-custodia
%license LICENSE
%exclude %{python3_sitelib}/custodia/store/etcdstore.py
%exclude %{python3_sitelib}/custodia/store/__pycache__/etcdstore.*
%{python3_sitelib}/*

%files -n python3-custodia-extra
%license LICENSE
%{python3_sitelib}/custodia/store/etcdstore.py
%{python3_sitelib}/custodia/store/__pycache__/etcdstore.*
%endif


%changelog
