%define target		avr
%define Werror_cflags	-Wformat
%define rel		2

Name:           cross-%{target}-gcc
Version:        4.6.2
Release:        %mkrel %rel
Summary:        Cross Compiling GNU GCC targeted at %{target}
Group:          Development/C
License:        GPLv2+
URL:            http://gcc.gnu.org/
Source0:        ftp://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-core-%{version}.tar.bz2
Source1:        ftp://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-g++-%{version}.tar.bz2
Patch0:		cross-avr-gcc-4.6.1-mint8.patch
BuildRequires:  cross-%{target}-binutils >= 2.21.1, zlib-devel gawk gmp-devel mpfr-devel libmpc-devel
Requires:       cross-%{target}-binutils >= 2.21.1
Obsoletes:      %{name}-cpp < %{version}
Provides:       %{name}-cpp = %{EVRD}

%description
This is a Cross Compiling version of GNU GCC, which can be used to
compile for the %{target} platform, instead of for the
native %{_arch} platform.


%package c++
Summary:        Cross Compiling GNU GCC targeted at %{target}
Group:          Development/C++
Requires:       %{name} = %{version}-%{release}

%description c++
This package contains the Cross Compiling version of g++, which can be used to
compile c++ code for the %{target} platform, instead of for the native %{_arch}
platform.


%prep
%setup -q -c
%setup -q -c -a 1
pushd gcc-%{?snapshot}%{!?snapshot:%version}

%patch0

contrib/gcc_update --touch
popd

# Extract %%__os_install_post into os_install_post~
cat << \EOF > os_install_post~
%__os_install_post
EOF

# Generate customized brp-*scripts
cat os_install_post~ | while read a x y; do
case $a in
# Prevent brp-strip* from trying to handle foreign binaries
*/brp-strip*)
  b=$(basename $a)
  sed -e 's,find %{buildroot},find %{buildroot}%_bindir %{buildroot}%_libexecdir,' $a > $b
  chmod a+x $b
  ;;
esac
done

sed -e 's,^[ ]*/usr/lib/rpm.*/brp-strip,./brp-strip,' \
< os_install_post~ > os_install_post 


%build
mkdir -p gcc-%{target}
pushd gcc-%{target}
CC="%{__cc} %optflags" \
../gcc-%{version}/configure --prefix=%{_prefix} --mandir=%{_mandir} \
  --infodir=%{_infodir} --target=%{target} --enable-languages=c,c++ \
  --disable-nls --disable-libssp --with-system-zlib \
  --enable-version-specific-runtime-libs \
  --with-pkgversion="Mandriva %{version}-%{release}" \
  --with-bugurl="https://qa.mandriva.com/" \
  --libexecdir=%{_libexecdir}
# In general, building GCC is not smp-safe
make
popd


%install
rm -rf %{buildroot}
pushd gcc-%{target}
make install DESTDIR=%{buildroot}
popd
# we don't want these as we are a cross version
rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_mandir}/man7
rm    %{buildroot}%{_libdir}/libiberty.a
# and these aren't usefull for embedded targets
rm -rf %{buildroot}/usr/lib/gcc/%{target}/%{version}/install-tools
rm -rf %{buildroot}%{_libexecdir}/gcc/%{target}/%{version}/install-tools

%define __os_install_post . ./os_install_post


%files
%defattr(-,root,root,-)
%doc gcc-%{version}/COPYING gcc-%{version}/COPYING.LIB
%{_bindir}/%{target}-*
%{_libexecdir}/gcc/%{target}/%{version}
%{_mandir}/man1/%{target}-*.1.xz
%exclude %{_bindir}/%{target}-?++
%exclude %{_libexecdir}/gcc/%{target}/%{version}/cc1plus
%exclude %{_mandir}/man1/%{target}-g++.1.xz

%files c++
%defattr(-,root,root,-)
%{_bindir}/%{target}-?++
%{_libexecdir}/gcc/%{target}/%{version}/cc1plus
%{_mandir}/man1/%{target}-g++.1.xz
