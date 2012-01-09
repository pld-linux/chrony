Summary:	An NTP client/server
Name:		chrony
Version:	1.26
Release:	4
License:	GPL v2
Group:		Daemons
URL:		http://chrony.tuxfamily.org/
Source0:	http://download.tuxfamily.org/chrony/%{name}-%{version}.tar.gz
# Source0-md5:	ad6dd619ff1986e4ff780363c64e2246
Source1:	%{name}.conf
Source2:	%{name}.keys
Source3:	%{name}d.sysconfig
Source4:	%{name}d.init
Source5:	%{name}.logrotate
Source6:	%{name}d.upstart
BuildRequires:	bison
BuildRequires:	libcap-devel
BuildRequires:	readline-devel
BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	texinfo
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Provides:	group(ntp)
Provides:	ntpdaemon
Provides:	user(ntp)
Obsoletes:	ntpdaemon
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/ntp

%description
A client/server for the Network Time Protocol, this program keeps your
computer's clock accurate. It was specially designed to support
systems with dial-up Internet connections, and also supports computers
in permanently connected environments.

%prep
%setup -q

%{__sed} -i -e 's,/usr/local,%{_prefix},g' *.texi

%build
# NOTE: It is not autoconf generated configre
CC="%{__cc}" \
CFLAGS="%{rpmcflags} -pie -fpie -Wmissing-prototypes -Wall" \
CPPFLAGS="%{rpmcppflags}" \
./configure \
	--prefix=%{_prefix} \
	--sysconfdir=%{_sysconfdir} \
	--docdir=%{_docdir} \
	--with-readline \
	--without-editline \

%{__make} getdate all docs

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,logrotate.d,rc.d/init.d,init} \
	$RPM_BUILD_ROOT{%{_sysconfdir},/var/{lib/ntp,log/chrony}}

%{__make} install install-docs \
	DESTDIR=$RPM_BUILD_ROOT

rm -rf $RPM_BUILD_ROOT%{_docdir}

cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/chrony.conf
cp -a %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/keys
cp -a %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/chronyd
cp -a %{SOURCE5} $RPM_BUILD_ROOT/etc/logrotate.d/chrony
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/rc.d/init.d/chronyd
cp -p %{SOURCE6} $RPM_BUILD_ROOT/etc/init/chronyd.conf

touch $RPM_BUILD_ROOT%{_localstatedir}/lib/ntp/{drift,rtc}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 246 ntp
%useradd -u 246 -d %{_localstatedir}/lib/ntp -g ntp -c "NTP Daemon" ntp

%post
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1
/sbin/chkconfig --add chronyd
%service chronyd restart

%preun
if [ "$1" = "0" ]; then
	%service chronyd stop
	/sbin/chkconfig --del chronyd
fi

%postun
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1
if [ "$1" = "0" ]; then
	%userremove ntp
	%groupremove ntp
fi

%files
%defattr(644,root,root,755)
%doc NEWS README chrony.txt faq.txt examples/*
%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/chrony.conf
%attr(640,root,ntp) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/keys
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/chronyd
%config(noreplace) %verify(not md5 mtime size) /etc/init/chronyd.conf
%config(noreplace) /etc/logrotate.d/chrony
%attr(754,root,root) /etc/rc.d/init.d/chronyd
%attr(755,root,root) %{_bindir}/chronyc
%attr(755,root,root) %{_sbindir}/chronyd
%{_mandir}/man1/chrony.1*
%{_mandir}/man1/chronyc.1*
%{_mandir}/man5/chrony.conf.5*
%{_mandir}/man8/chronyd.8*
%{_infodir}/chrony.info*

%dir %attr(770,root,ntp) /var/lib/ntp
%attr(640,ntp,ntp) %ghost /var/lib/ntp/drift
%attr(640,ntp,ntp) %ghost /var/lib/ntp/rtc

%dir %attr(770,ntp,ntp) /var/log/chrony
