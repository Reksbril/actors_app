from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class FileFieldVerifier:
    class FileVerificationError(RuntimeError):
        pass

    def __init__(self, content_types, max_size):
        self.content_types = content_types
        self.max_size = max_size

    """
    Verifies if content type and size are supported. If they are, return True. If they aren't throw FileVerificationError.
    """

    def verify(self, content_type, size):
        if content_type not in self.content_types:
            raise FileFieldVerifier.FileVerificationError(
                _(
                    f"Filetype not supported. Supported file types: {self.content_types}, got {content_type}"
                )
            )
        if size > self.max_size:
            raise FileFieldVerifier.FileVerificationError(
                _("Please keep filesize under %s. Current filesize %s")
                % (filesizeformat(self.max_size), filesizeformat(size))
            )

        return True


class ContentTypeRestrictedFileField(forms.FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB - 104857600
            250MB - 214958080
            500MB - 429916160
    """

    def __init__(self, *args, **kwargs):
        content_types = kwargs.pop("content_types", [])
        max_upload_size = kwargs.pop("max_upload_size", 0)
        self.file_field_verifier = FileFieldVerifier(
            content_types=content_types, max_size=max_upload_size
        )

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        try:
            self.file_field_verifier.verify(
                content_type=data.content_type, size=data.size
            )
        except FileFieldVerifier.FileVerificationError as e:
            logger.error(f"Error during form validation: {e}")
            raise forms.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unknown error duringn form validation: {e}")
            raise forms.ValidationError(_("Unknown error occured"))

        return data


class PdfFileForm(forms.Form):
    scenario_id = forms.CharField(label="Scenario ID", max_length=200)
    file = ContentTypeRestrictedFileField(
        label="PDF file",
        allow_empty_file=False,
        max_upload_size=settings.MAX_PDF_UPLOAD_SIZE_BYTES,
        content_types=["application/pdf"],
    )
