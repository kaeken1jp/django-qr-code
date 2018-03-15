"""Tools for generating QR codes. This module depends on the qrcode python library."""

import base64
from io import BytesIO

import xml.etree.ElementTree as ET

from django.utils.html import escape
from django.utils.safestring import mark_safe

from qr_code.qrcode.constants import SIZE_DICT, ERROR_CORRECTION_DICT, DEFAULT_MODULE_SIZE, \
    DEFAULT_BORDER_SIZE, DEFAULT_VERSION, DEFAULT_ERROR_CORRECTION
from qr_code.qrcode.image import SvgPathImage, PilImageOrFallback, SVG_FORMAT_NAME, PNG_FORMAT_NAME
from qr_code.qrcode.utils import QRCodeOptions
from qr_code.qrcode.serve import make_qr_code_url


class SvgEmbeddedInHtmlImage(SvgPathImage):
    def _write(self, stream):
        self._img.append(self.make_path())
        ET.ElementTree(self._img).write(stream, encoding="UTF-8", xml_declaration=False, default_namespace=None,
                                        method='html')


def make_qr_code_image(text, image_factory, size=DEFAULT_MODULE_SIZE, border=DEFAULT_BORDER_SIZE, version=DEFAULT_VERSION, error_correction=DEFAULT_ERROR_CORRECTION):
    """
    Generates an image object (from the qrcode library) representing the QR code for the given text.

    Any invalid argument is silently converted into the default value for that argument.

    See the function :func:`~qr_code.qr_code.make_embedded_qr_code` for behavior and details about parameters meaning.
    """

    if isinstance(version, int) or (isinstance(version, str) and version.isdigit()):
        actual_version = int(version)
        if actual_version < 1 or actual_version > 40:
            actual_version = 0
    else:
        actual_version = 0
    if isinstance(size, int) or (isinstance(size, str) and size.isdigit()):
        actual_size = int(size)
        if actual_size < 1:
            actual_size = SIZE_DICT['m']
    else:
        if not size or not size.lower() in SIZE_DICT:
            size = 'm'
        actual_size = SIZE_DICT[size.lower()]
    import qrcode
    qr = qrcode.QRCode(
        version=actual_version if actual_version != 0 else 1,
        error_correction=ERROR_CORRECTION_DICT.get(error_correction.upper(), ERROR_CORRECTION_DICT[
            DEFAULT_ERROR_CORRECTION]),
        box_size=actual_size,
        border=border
    )
    qr.add_data(text)
    if actual_version == 0:
        qr.make(fit=True)
    return qr.make_image(image_factory=image_factory)


def make_qr_code(embedded, text, qr_code_options):
    if embedded is True:
        return make_embedded_qr_code(text, qr_code_options)
    return make_qr_code_url(text, qr_code_options)


def make_embedded_qr_code(text, qr_code_options=QRCodeOptions()):
    """
    Generates a <svg> or <img> tag representing the QR code for the given text. This tag can be embedded into an
    HTML document.
    """
    image_format = qr_code_options.image_format
    img = make_qr_code_image(text, SvgEmbeddedInHtmlImage if image_format == SVG_FORMAT_NAME else PilImageOrFallback, size=qr_code_options.size, border=qr_code_options.border, version=qr_code_options.version, error_correction=qr_code_options.error_correction)
    stream = BytesIO()
    if image_format == SVG_FORMAT_NAME:
        img.save(stream, kind=SVG_FORMAT_NAME.upper())
        html_fragment = (str(stream.getvalue(), 'utf-8'))
    else:
        img.save(stream, format=PNG_FORMAT_NAME.upper())
        html_fragment = '<img src="data:image/png;base64, %s" alt="%s"' % (str(base64.b64encode(stream.getvalue()), encoding='ascii'), escape(text))
    return mark_safe(html_fragment)


