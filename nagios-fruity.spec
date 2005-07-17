Summary:	Nagios Configuration Tool
Summary(pl):	Narzêdzie konfiguracyjne dla Nagiosa
Name:		nagios-fruity
Version:	1.0
%define		_beta beta1
%define		_rc	pl2
Release:	0.%{_beta}.%{_rc}.14
Epoch:		0
License:	GPL v2
Group:		Applications/WWW
Source0:	http://dl.sourceforge.net/fruity/fruity-%{version}-%{_beta}-%{_rc}.tar.gz
# Source0-md5:	f53a6aa9bf38b0bd01c640f51312cc8c
URL:		http://fruity.sourceforge.net/
BuildRequires:	rpmbuild(macros) >= 1.226
BuildRequires:	sed >= 4.0
Requires:	adodb
Requires:	nagios >= 2.0
Requires:	php >= 5.0.0
Requires:	php-mysql
Requires:	php-pear-HTML_TreeMenu
Requires:	webserver = apache
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir %{_datadir}/fruity

%description
A Nagios Configuration Tool.

%description
Narzêdzie konfiguracyjne dla Nagiosa.

%prep
%setup -q -n fruity
rm -rf CVS
rm -rf config # no longer used

# undos the source
find '(' -name '*.php' -o -name '*.inc' ')' -print0 | xargs -0 sed -i -e 's,
$,,'

mv includes/config.inc{,.dist}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_appdir},%{_sysconfdir}}

cp -a *.php *.js $RPM_BUILD_ROOT%{_appdir}
cp -a images includes modules output session sitedb style $RPM_BUILD_ROOT%{_appdir}

cat <<EOF > $RPM_BUILD_ROOT%{_sysconfdir}/apache-fruity.conf
Alias /fruity %{_appdir}
<Location /fruity>
	allow from all
	php_value short_open_tag on
</Location>
# vim: filetype=apache ts=4 sw=4 et
EOF

sed -e "
s,/usr/local/groundwork/fruity/logos,/usr/share/nagios/images/logos,
s,/usr/local/groundwork/fruity,/usr/share/fruity,
s,sitedb_config\[.username.\].=.'root',sitedb_config['username'] = 'mysql',
" includes/config.inc.dist > $RPM_BUILD_ROOT%{_appdir}/includes/config.inc

rm -f $RPM_BUILD_ROOT%{_appdir}/includes/config.inc.dist

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = 1 ]; then
	%banner %{name} <<-EOF
	You need to create mysql database 'fruity':
	mysqladmin create fruity
	zcat %{_docdir}/%{name}-%{version}/fruity-mysql.sql.gz | mysql fruity
EOF
fi

%triggerin -- apache1 >= 1.3.33-2
%apache_config_install -v 1 -c %{_sysconfdir}/apache-fruity.conf

%triggerun -- apache1 >= 1.3.33-2
%apache_config_uninstall -v 1

%triggerin -- apache >= 2.0.0
%apache_config_install -v 2 -c %{_sysconfdir}/apache-fruity.conf

%triggerun -- apache >= 2.0.0
%apache_config_uninstall -v 2

%files
%defattr(644,root,root,755)
%doc INSTALL sqldata/*
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache-fruity.conf
%{_appdir}
