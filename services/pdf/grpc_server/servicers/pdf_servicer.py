class PdfServicer:
    """gRPC servicer stub for the PDF service.

    All methods return valid placeholder responses.
    Full implementations will be added in later milestones.
    """

    def GeneratePdf(self, request, context):  # type: ignore[no-untyped-def]
        return {"pdf_data": b"", "filename": "placeholder.pdf"}
