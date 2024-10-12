from django.test import TestCase

from pdf_app.forms import FileFieldVerifier


class FormsTest(TestCase):
    def test_verifier_happy_path(self):
        verifier = FileFieldVerifier(content_types=["pdf"], max_size=10)

        assert verifier.verify(content_type="pdf", size=1)

    def test_verifier_not_suppored_content_type(self):
        verifier = FileFieldVerifier(content_types=["pdf"], max_size=10)

        with self.assertRaisesRegex(
            FileFieldVerifier.FileVerificationError, "Filetype not supported"
        ):
            verifier.verify(content_type="png", size=1)

    def test_verifier_too_big_file_size(self):
        verifier = FileFieldVerifier(content_types=["pdf"], max_size=10)

        with self.assertRaisesRegex(
            FileFieldVerifier.FileVerificationError, "Please keep filesize under"
        ):
            verifier.verify(content_type="pdf", size=11)
