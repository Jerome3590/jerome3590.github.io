---
description: DuckDB extension pattern for Lambda ECR images
alwaysApply: true
---

# DuckDB Lambda Extension Pattern

- For Lambda container images that use DuckDB, follow the OSI supply-chain-risk ECR pattern.
- Install DuckDB and heavy data dependencies into `${LAMBDA_TASK_ROOT}` during image build.
- Preinstall required DuckDB extensions in the Dockerfile, then copy `~/.duckdb/extensions` into `${LAMBDA_TASK_ROOT}/extensions`.
- Set `DUCKDB_EXTENSION_PATH="${LAMBDA_TASK_ROOT}/extensions"` in the image.
- Runtime code should set DuckDB `home_directory`, `extension_directory`, and `temp_directory`, then `LOAD` preinstalled extensions.
- Do not rely on runtime `INSTALL` for Lambda execution paths.

Example:

```dockerfile
RUN pip install duckdb==1.2.1 pyarrow==19.0.1 numpy==2.2.4 pandas==2.2.3 --target "${LAMBDA_TASK_ROOT}"
RUN mkdir -p "${LAMBDA_TASK_ROOT}/extensions"
RUN python3 -c "import duckdb; duckdb.sql('INSTALL httpfs; LOAD httpfs; INSTALL duckpgq FROM community; LOAD duckpgq;')"
RUN cp -r ~/.duckdb/extensions "${LAMBDA_TASK_ROOT}/"
ENV DUCKDB_EXTENSION_PATH="${LAMBDA_TASK_ROOT}/extensions"
```
