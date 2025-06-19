%define		nettle_ver	3.9

Summary:	An NTP client/server
Summary(pl.UTF-8):	Klient/serwer NTP
Name:		chrony
Version:	4.7
Release:	1
License:	GPL v2
Group:		Daemons
Source0:	https://chrony-project.org/releases/%{name}-%{version}.tar.gz
# Source0-md5:	a1ab6e972527a9cbf6bf862679352ed3
Source1:	%{name}.conf
Source2:	%{name}.keys
Source3:	%{name}d.sysconfig
Source4:	%{name}d.init
Source5:	%{name}.logrotate
Patch0:		fix-seccomp-build.patch
Patch1:		conf.d.patch
URL:		https://chrony-project.org/
BuildRequires:	asciidoc
BuildRequires:	bison
BuildRequires:	gnutls-devel
BuildRequires:	libcap-devel
BuildRequires:	libedit-devel
BuildRequires:	libseccomp-devel
# for hashing; can be also nss 3.x, libtomcrypt, gnutls
BuildRequires:	nettle-devel >= %{nettle_ver}
BuildRequires:	pkgconfig
BuildRequires:	pps-tools-devel
BuildRequires:	rpmbuild(macros) >= 1.453
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Provides:	group(ntp)
Provides:	ntpdaemon
Provides:	user(ntp)
Requires:	nettle >= %{nettle_ver}
Obsoletes:	ntpdaemon
Conflicts:	logrotate < 3.8.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/ntp

# assume gcc 3.4 has it
%if "%{cc_version}" >= "3.4"
%define		specflags	-pie -fpie
%endif

%description
A client/server for the Network Time Protocol, this program keeps your
computer's clock accurate. It was specially designed to support
systems with dial-up Internet connections, and also supports computers
in permanently connected environments.

%description -l pl.UTF-8
Klient/serwer protokołu NTP (Network Time Protocol), pozwalający
utrzymać zegar komputera dokładnym. Został zaprojektowany w
szczególności do obsłużenia systemów z wdzwanianym połączeniem do
Internetu, obsługuje także komputery na stałym łączu.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1

%build
# NOTE: It is not autoconf generated configre
CC="%{__cc}" \
CFLAGS="%{rpmcflags} -Wmissing-prototypes -Wall" \
CPPFLAGS="%{rpmcppflags}" \
./configure \
	--enable-debug \
	--enable-ntp-signd \
	--enable-scfilter \
	--prefix=%{_prefix} \
	--sysconfdir=%{_sysconfdir} \
	--docdir=%{_docdir} \
	--with-ntp-era=$(date -d '1970-01-01 00:00:00+00:00' +'%s') \
	--with-hwclockfile=%{_sysconfdir}/adjtime \
	--with-sendmail=%{_sbindir}/sendmail

%{__make} getdate all docs \
	ADOC=asciidoc

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,logrotate.d,rc.d/init.d} \
	$RPM_BUILD_ROOT{%{_sysconfdir}/chrony.d,/var/{lib/ntp,log/chrony}}

%{__make} install install-docs \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm} -r $RPM_BUILD_ROOT%{_docdir}

cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/chrony.conf
cp -a %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/keys
cp -a %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/chronyd
cp -a %{SOURCE5} $RPM_BUILD_ROOT/etc/logrotate.d/chrony
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/rc.d/init.d/chronyd

touch $RPM_BUILD_ROOT%{_localstatedir}/lib/ntp/{drift,rtc}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 246 ntp
%useradd -u 246 -d %{_localstatedir}/lib/ntp -g ntp -c "NTP Daemon" ntp

%post
/sbin/chkconfig --add chronyd
%service chronyd restart

%preun
if [ "$1" = "0" ]; then
	%service chronyd stop
	/sbin/chkconfig --del chronyd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove ntp
	%groupremove ntp
fi

%files
%defattr(644,root,root,755)
%doc NEWS README FAQ examples/* doc/{faq,installation}.html
%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/chrony.conf
%attr(750,root,root) %dir %{_sysconfdir}/chrony.d
%attr(640,root,ntp) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/keys
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/chronyd
%config(noreplace) /etc/logrotate.d/chrony
%attr(754,root,root) /etc/rc.d/init.d/chronyd
%attr(755,root,root) %{_bindir}/chronyc
%attr(755,root,root) %{_sbindir}/chronyd
%{_mandir}/man1/chronyc.1*
%{_mandir}/man5/chrony.conf.5*
%{_mandir}/man8/chronyd.8*

%dir %attr(770,root,ntp) /var/lib/ntp
%attr(640,ntp,ntp) %ghost /var/lib/ntp/drift
%attr(640,ntp,ntp) %ghost /var/lib/ntp/rtc

%dir %attr(770,ntp,ntp) /var/log/chrony
