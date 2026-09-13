"""Konfigurasi terpusat NADI.

Seluruh pengaturan dibaca dari variabel lingkungan berawalan ``NADI_``
atau dari berkas ``.env`` di akar proyek. Tidak ada nilai rahasia yang
ditulis langsung di dalam kode.
"""

from __future__ import annotations

import secrets
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/nadi/config.py -> nadi -> backend -> akar proyek
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Pengaturan aplikasi yang divalidasi saat proses dimulai."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        env_prefix="NADI_",
        extra="ignore",
        case_sensitive=False,
    )

    # ---------- Aplikasi ----------
    app_name: str = "NADI - Navigasi AI Data Intervensi"
    app_version: str = "0.1.0"
    env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    )

    # ---------- Keamanan ----------
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 480

    # ---------- Basis data ----------
    database_url: str = "sqlite:///./data/nadi.db"
    db_echo: bool = False

    # ---------- Layanan AI ----------
    llm_enabled: bool = True
    llm_base_url: str = "https://opencode.ai/zen/v1"
    llm_api_key: str = ""
    llm_model: str = ""
    llm_timeout_seconds: float = 60.0
    llm_max_tokens: int = 2400
    llm_temperature: float = 0.2

    # ---------- Privasi ----------
    llm_block_pii: bool = True
    pseudonymize: bool = True

    # ---------- Reproduktifitas ----------
    random_seed: int = 20260913  # tanggal batas akhir LAN Datathon 2026

    # ---------------------------------------------------------------
    # Validator
    # ---------------------------------------------------------------
    @field_validator("secret_key")
    @classmethod
    def _reject_placeholder_secret(cls, v: str) -> str:
        if v.startswith("ganti-nilai-ini"):
            raise ValueError(
                "NADI_SECRET_KEY masih berisi nilai contoh. Hasilkan kunci nyata dengan:\n"
                '  python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        if len(v) < 32:
            raise ValueError("NADI_SECRET_KEY terlalu pendek (minimal 32 karakter).")
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # ---------------------------------------------------------------
    # Lintasan berkas turunan
    # ---------------------------------------------------------------
    @property
    def project_root(self) -> Path:
        return PROJECT_ROOT

    @property
    def data_dir(self) -> Path:
        return PROJECT_ROOT / "data"

    @property
    def seed_dir(self) -> Path:
        return self.data_dir / "seed"

    @property
    def generated_dir(self) -> Path:
        return self.data_dir / "generated"

    @property
    def geo_dir(self) -> Path:
        return self.data_dir / "geo"

    @property
    def models_dir(self) -> Path:
        return PROJECT_ROOT / "models" / "artifacts"

    @property
    def frontend_dist(self) -> Path:
        return PROJECT_ROOT / "frontend" / "dist"

    @property
    def llm_configured(self) -> bool:
        """Benar hanya bila layanan AI benar-benar siap dipanggil.

        Kunci yang masih berisi teks contoh dan nama model yang kosong sama
        saja dengan belum dikonfigurasi. Melaporkannya sebagai siap akan
        membuat kegagalan baru terlihat saat demo berlangsung.
        """
        return bool(
            self.llm_enabled
            and self.llm_base_url
            and self.llm_model.strip()
            and self.llm_api_key.strip()
            and not self.llm_api_key.strip().startswith("isi-api-key")
        )

    @property
    def alasan_llm_belum_siap(self) -> str | None:
        """Penjelasan singkat mengapa layanan AI belum siap, atau ``None``."""
        if not self.llm_enabled:
            return "NADI_LLM_ENABLED bernilai false."
        if not self.llm_base_url:
            return "NADI_LLM_BASE_URL belum diisi."
        if not self.llm_api_key.strip() or self.llm_api_key.strip().startswith("isi-api-key"):
            return "NADI_LLM_API_KEY belum diisi pada berkas .env."
        if not self.llm_model.strip():
            return "NADI_LLM_MODEL belum diisi pada berkas .env."
        return None

    def ensure_directories(self) -> None:
        for d in (self.data_dir, self.seed_dir, self.generated_dir, self.geo_dir, self.models_dir):
            d.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Kembalikan satu instans pengaturan yang di-cache untuk seluruh proses."""
    return Settings()


settings = get_settings()
