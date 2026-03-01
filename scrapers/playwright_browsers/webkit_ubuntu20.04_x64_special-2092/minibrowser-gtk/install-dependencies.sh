#!/bin/bash
set -eu -o pipefail

REQUIREDPACKAGES="libgcrypt20:amd64 libpangoft2-1.0-0:amd64 libopenexr24:amd64 libxcb-shm0:amd64 libdrm-amdgpu1:amd64 libc6:amd64 libxrandr2:amd64 libevdev2:amd64 libsystemd0:amd64 libopus0:amd64 libjson-glib-1.0-0:amd64 libxau6:amd64 libgl1-mesa-dri:amd64 libxi6:amd64 libvorbisenc2:amd64 libpsl5:amd64 libfdk-aac1:amd64 libudev1:amd64 libproxy1v5:amd64 libusb-1.0-0:amd64 libsecret-1-0:amd64 libpulse0:amd64 libglapi-mesa:amd64 libxext6:amd64 libasound2:amd64 libegl1:amd64 libhyphen0:amd64 libvorbis0a:amd64 libdrm-intel1:amd64 liblcms2-2:amd64 libthai0:amd64 libharfbuzz0b:amd64 libharfbuzz-icu0:amd64 libgles2:amd64 libxcomposite1:amd64 libjpeg-turbo8:amd64 libxinerama1:amd64 libkate1:amd64 libnghttp2-14:amd64 libv4lconvert0:amd64 libpcre2-8-0:amd64 libapparmor1:amd64 libsqlite3-0:amd64 libmpg123-0:amd64 libegl-mesa0:amd64 librsvg2-2:amd64 libstdc++6:amd64 libcairo-gobject2:amd64 libxml2:amd64 libvpx6:amd64 libwebpmux3:amd64 libgpg-error0:amd64 libgraphite2-3:amd64 libilmbase24:amd64 libpng16-16:amd64 libxdamage1:amd64 libopenjp2-7:amd64 libdrm-nouveau2:amd64 libtheora0:amd64 libsndfile1:amd64 libcairo2:amd64 libicu66:amd64 libflac8:amd64 libxcb-render0:amd64 libgtk-3-0:amd64 libatomic1:amd64 libgdk-pixbuf2.0-0:amd64 libxdmcp6:amd64 libogg0:amd64 libwoff1:amd64 libexpat1:amd64 libdbus-1-3:amd64 libunistring2:amd64 libxcursor1:amd64 libhogweed5:amd64 liblzma5:amd64 libenchant-2-2:amd64 libepoxy0:amd64 libidn2-0:amd64 libglx0:amd64 libevent-2.1-7:amd64 libuuid1:amd64 libtasn1-6:amd64 libwebp6:amd64 libx11-6:amd64 libpixman-1-0:amd64 libfribidi0:amd64 libgnutls30:amd64 libxslt1.1:amd64 libdc1394-22:amd64 libdrm-radeon1:amd64 libnettle7:amd64 libffi7:amd64 libgl1:amd64 libv4l-0:amd64 libglx-mesa0:amd64 libp11-kit0:amd64 libpango-1.0-0:amd64 libpangocairo-1.0-0:amd64 libgmp10:amd64 libgbm1:amd64 libwebpdemux2:amd64 libxfixes3:amd64 libdatrie1:amd64 libgcc-s1:amd64 libbsd0:amd64 libfontconfig1:amd64 libasyncns0:amd64 libwrap0:amd64 libflite1:amd64 libdrm2:amd64 libraw1394-11:amd64 libxrender1:amd64 libx11-xcb1:amd64 libssl1.1:amd64 zlib1g:amd64 ca-certificates libgudev-1.0-0:amd64 shared-mime-info libxcb1:amd64 libfreetype6:amd64 liblz4-1:amd64 libglvnd0:amd64"

if ! which apt-get >/dev/null; then
    echo "This script only supports apt-get based distributions like Debian or Ubuntu."
    exit 1
fi

# Calling dpkg-query is slow, so call it only once and cache the results
TMPCHECKPACKAGES="$(mktemp)"
dpkg-query --show --showformat='${binary:Package} ${db:Status-Status}\n' > "${TMPCHECKPACKAGES}"
TOINSTALL=""
for PACKAGE in ${REQUIREDPACKAGES}; do
    if ! grep -qxF "${PACKAGE} installed" "${TMPCHECKPACKAGES}"; then
        TOINSTALL="${TOINSTALL} ${PACKAGE}"
    fi
done
rm -f "${TMPCHECKPACKAGES}"

if [[ -z "${TOINSTALL}" ]]; then
    echo "All required dependencies are already installed"
else
    echo "Need to install the following extra packages: ${TOINSTALL}"
    [[ ${#} -gt 0 ]] && [[ "${1}" == "--printonly" ]] && exit 0
    SUDO=""
    [[ ${UID} -ne 0 ]] && SUDO="sudo"
    AUTOINSTALL=""
    if [[ ${#} -gt 0 ]] && [[ "${1}" == "--autoinstall" ]]; then
        AUTOINSTALL="-y"
        export DEBIAN_FRONTEND="noninteractive"
        [[ ${UID} -ne 0 ]] && SUDO="sudo --preserve-env=DEBIAN_FRONTEND"
        ${SUDO} apt-get update
    fi
    set -x
    ${SUDO} apt-get install --no-install-recommends ${AUTOINSTALL} ${TOINSTALL}
fi
