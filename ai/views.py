import json
import logging
import os
import tempfile
from pathlib import Path

from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .resume_parser import parse_resume

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class ResumeParseView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        uploaded = request.FILES.get("resume")
        if uploaded is None:
            return Response(
                {"error": "No file uploaded. Send it in the 'resume' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        suffix = Path(uploaded.name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            return Response(
                {"error": "Only PDF and DOCX files are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if uploaded.size > MAX_FILE_SIZE:
            return Response(
                {"error": "File is too large (max 5 MB)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in uploaded.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            data = parse_resume(tmp_path)
        except json.JSONDecodeError:
            logger.exception("Model returned invalid JSON")
            return Response(
                {"error": "AI returned an invalid response. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Resume parsing failed")
            return Response(
                {"error": "Resume parsing failed. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        finally:
            os.remove(tmp_path)

        return Response(data, status=status.HTTP_200_OK)
