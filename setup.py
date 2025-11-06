from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="edge-tts",
    install_requires=[
        "aiohttp>=3.8.0,<4.0.0",
        "certifi>=2023.11.17",
        "tabulate>=0.4.4,<1.0.0",
        "typing-extensions>=4.1.0,<5.0.0",
    ],
    extras_require={
        "server": [
            "fastapi>=0.104.0,<1.0.0",
            "uvicorn>=0.24.0,<1.0.0",
            "pydantic>=2.0.0,<3.0.0",
        ],
    },
)
