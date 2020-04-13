License:        BSD
Vendor:         Otus
Group:          PD01
URL:            http://otus.ru/lessons/3/
Source0:        otus-%{current_datetime}.tar.gz
BuildRoot:      %{_tmppath}/otus-%{current_datetime}
Name:           ip2w
Version:        0.0.1
Release:        1
BuildArch:      noarch
Requires:       python3
Requires:       python3-requests
Requires:       uwsgi
Requires:       uwsgi-plugin-python36.x86_64
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
Requires:	
Summary:  IP to weather WSGI daemon


%description
Homework to "Python developer" course
Git version: %{git_version} (branch: %{git_branch})

%define __etcdir    /usr/local/etc
%define __logdir    /val/log/
%define __bindir    /usr/local/ip2w/
%define __systemddir	/usr/lib/systemd/system/
%define __sockdir       /var/local/ip2w/

%prep
rm -rf %{buildroot}
%setup -n otus-%{current_datetime}

%install
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}
%{__mkdir} -p %{buildroot}/%{__systemddir}
%{__mkdir} -p %{buildroot}/%{__logdir}
%{__mkdir} -p %{buildroot}/%{__bindir}
%{__mkdir} -p %{buildroot}/%{__etcdir}
%{__mkdir} -p %{buildroot}/%{__sockdir}

%{__install} -pD -m 644 ip2w.service %{buildroot}/%{__systemddir}/%{name}.service
%{__install} -pD -m 755 ip2w_app.py %{buildroot}/%{__bindir}/ip2w_app.py
%{__install} -pD -m 644 ip2w_uwsgi.ini %{buildroot}/%{__etcdir}/ip2w_uwsgi.ini
%{__install} -pD -m 644 settings.py %{buildroot}/%{__etcdir}/settings.py


%post
%systemd_post %{name}.service
systemctl daemon-reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%clean
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}


%files
%{__logdir}
%{__bindir}/*
%{__systemddir}/%{name}.service
%{__sockdir}
# %{__sysconfigdir}
%config(noreplace) %{__etcdir}/settings.py
%config(noreplace) %{__etcdir}/ip2w_uwsgi.ini