Name:           jna
Version:        3.2.4
Release:        2%{?dist}
Summary:        Pure Java access to native libraries

Group:          Development/Libraries
License:        LGPLv2+
URL:            https://jna.dev.java.net/
# The source for this package was pulled from upstream's vcs. Use the
# following commands to generate the tarball:
#   svn export https://jna.dev.java.net/svn/jna/tags/%{version}/jnalib/ --username guest jna-%{version}
#   rm jna-%{version}/dist/*
#   tar -cjf jna-%{version}.tar.bz2 jna-%{version}
Source0:        %{name}-%{version}.tar.bz2
# This patch is Fedora-specific for now until we get the huge
# JNI library location mess sorted upstream
Patch1:         jna-3.2.4-loadlibrary.patch
# The X11 tests currently segfault; overall I think the X11 JNA stuff is just a 
# Really Bad Idea, for relying on AWT internals, using the X11 API at all,
# and using a complex API like X11 through JNA just increases the potential
# for problems.
Patch2:         jna-3.2.4-tests-headless.patch
# Upstream appears to have some sort of MD5 check on the contents of their
# native jar.  Carve that out so we always build it.
Patch3:         jna-3.2.4-build-md5.patch
# Build using GCJ javadoc
Patch4:         jna-3.2.4-gcj-javadoc.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  java-devel ant jpackage-utils ant-nodeps
BuildRequires:  libX11-devel libXt-devel libffi-devel
# We manually require libffi because find-requires doesn't work
# inside jars.
Requires:       java jpackage-utils libffi
# for ExcludeArch see bug: 468831
%if 0%{?rhel} < 6
ExcludeArch: ppc ppc64
%endif


%description
JNA provides Java programs easy access to native shared libraries
(DLLs on Windows) without writing anything but Java code. JNA's
design aims to provide native access in a natural way with a
minimum of effort. No boilerplate or generated code is required.
While some attention is paid to performance, correctness and ease
of use take priority.


%package        javadoc
Summary:        Javadocs for %{name}
Group:          Documentation
Requires:       %{name} = %{version}-%{release}


%description    javadoc
This package contains the javadocs for %{name}.


%package        examples
Summary:        Examples for %{name}
Group:          Documentation
Requires:       %{name} = %{version}-%{release}


%description    examples
This package contains the examples for %{name}.


%prep
%setup -q -n %{name}-%{version}
sed -e 's|@JNIPATH@|%{_libdir}/%{name}|' %{PATCH1} | patch -p1
%patch2 -p1 -b .tests-headless
%patch3 -p0 -R -b .md5
%patch4 -p0 -b .gcj-javadoc

# all java binaries must be removed from the sources
find . -name '*.jar' -exec rm -f '{}' \;
find . -name '*.class' -exec rm -f '{}' \;

# remove internal copy of libffi
rm -rf native/libffi

# clean LICENSE.txt
sed -i 's/\r//' LICENSE.txt
chmod 0644 LICENSE.txt


%build
# We pass -Ddynlink.native which comes from our patch because
# upstream doesn't want to default to dynamic linking.
ant -Dcflags_extra.native="%{optflags}" -Ddynlink.native=true -Dnomixedjar.native=true jar examples
ant javadoc


%install
rm -rf %{buildroot}

# jars
install -D -m 644 build*/%{name}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
install -D -m 644 build*/examples.jar %{buildroot}%{_javadir}/%{name}-examples-%{version}.jar
(cd %{buildroot}%{_javadir}/; for jar in `ls *-%{version}.jar`; do ln -s $jar `echo $jar | sed -e 's/-%{version}//'`; done)
# NOTE: JNA has highly custom code to look for native jars in this
# directory.  Since this roughly matches the jpackage guidelines,
# we'll leave it unchanged.
install -d -m 755 %{buildroot}%{_libdir}/%{name}
install -m 755 build*/native/libjnidispatch*.so %{buildroot}%{_libdir}/%{name}/

# javadocs
install -p -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -a doc/javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc LICENSE.txt
%{_libdir}/%{name}
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar


%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}-%{version}


%files examples
%defattr(-,root,root,-)
%{_javadir}/%{name}-examples.jar
%{_javadir}/%{name}-examples-%{version}.jar


%changelog
* Wed Apr 28 2010 Deepak Bhole <dbhole@redhat.com> 3.2.4-2
- Import Colin Walters' gcj build changes from Fedora spec file

* Sat Nov 14 2009 Levente Farkas <lfarkas@lfarkas.org> - 3.2.4-1
- Rebase on upstream 3.2.4

* Thu Oct 29 2009 Lubomir Rintel <lkundrak@v3.sk> - 3.0.9-6
- Add examples subpackage

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.9-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.9-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Dec 30 2008 Colin Walters <walters@redhat.com> - 3.0.9-3
- Add patch to allow opening current process

* Sun Nov 30 2008 Colin Walters <walters@redhat.com> - 3.0.9-2
- Fix library mapping, remove upstreamed patches

* Fri Oct 31 2008 Colin Walters <walters@redhat.com> - 3.0.9-1
- Rebase on upstream 3.0.9

* Tue Oct 14 2008 Colin Walters <walters@redhat.com> - 3.0.4-10.svn729
- Add patch to support String[] returns

* Wed Oct 01 2008 Colin Walters <walters@redhat.com> - 3.0.4-9.svn729
- Add new patch to support NativeMapped[] which I want

* Wed Oct 01 2008 Colin Walters <walters@redhat.com> - 3.0.4-8.svn729
- Update to svn r729
- drop upstreamed typemapper patch

* Tue Sep 18 2008 Colin Walters <walters@redhat.com> - 3.0.4-7.svn700
- Add patch to make typemapper always accessible
- Add patch to skip cracktastic X11 test bits which currently fail

* Tue Sep 09 2008 Colin Walters <walters@redhat.com> - 3.0.4-5.svn700
- Update to upstream SVN r700; drop all now upstreamed patches

* Sat Sep 06 2008 Colin Walters <walters@redhat.com> - 3.0.4-3.svn630
- A few more patches for JGIR

* Thu Sep 04 2008 Colin Walters <walters@redhat.com> - 3.0.4-2.svn630
- Add two (sent upstream) patches that I need for JGIR

* Thu Jul 31 2008 Colin Walters <walters@redhat.com> - 3.0.4-1.svn630
- New upstream version, drop upstreamed patch parts
- New patch jna-3.0.4-nomixedjar.patch which ensures that we don't
  include the .so in the .jar

* Fri Apr 04 2008 Colin Walters <walters@redhat.com> - 3.0.2-7
- Add patch to use JPackage-compatible JNI library path
- Do build debuginfo package
- Refactor build patch greatly so it's hopefully upstreamable
- Install .so directly to JNI directory, rather than inside jar
- Clean up Requires/BuildRequires (thanks Mamoru Tasaka)

* Sun Mar 30 2008 Conrad Meyer <konrad@tylerc.org> - 3.0.2-6
- -javadocs should be -javadoc.
- %%files section cleaned a bit.

* Mon Mar 17 2008 Conrad Meyer <konrad@tylerc.org> - 3.0.2-5
- -javadocs package should be in group "Documentation".

* Mon Mar 17 2008 Conrad Meyer <konrad@tylerc.org> - 3.0.2-4
- License should be LGPLv2+, not GPLv2+.
- Several minor fixes.
- Fix Requires in javadoc package.

* Sun Mar 16 2008 Conrad Meyer <konrad@tylerc.org> - 3.0.2-3
- Don't use internal libffi.

* Thu Mar 6 2008 Conrad Meyer <konrad@tylerc.org> - 3.0.2-2
- Don't pull in jars from the web.

* Mon Mar 3 2008 Conrad Meyer <konrad@tylerc.org> - 3.0.2-1
- Initial package.
