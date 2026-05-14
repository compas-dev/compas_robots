# Installation

This chapter provides a step-by-step guide for installing `compas_robots` on your system.
We highly recommend using [uv](https://docs.astral.sh/uv/) for managing
your Python environment and dependencies, as it is significantly faster and
more reliable. Alternatively, you can use standard `pip` or `conda`.

## Install uv

If you do not have `uv` installed, follow the instructions on their website or run:

=== "Mac/Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

## Create a virtual environment

It is best practice to install `compas_robots` in a virtual environment.
Navigate to your project directory and run:

```bash
uv venv
```

This creates a virtual environment in `.venv`. Activate it with:

=== "Mac/Linux"

    ```bash
    source .venv/bin/activate
    ```

=== "Windows"

    ```powershell
    .venv\Scripts\activate
    ```

## Install compas_robots

With your virtual environment activated, install `compas_robots`:

```bash
uv pip install compas_robots
```

Or, if you prefer `pip`:

```bash
pip install compas_robots
```

Or, with `conda` from the `conda-forge` channel:

```bash
conda install -c conda-forge compas_robots
```

## Verify installation

Verify that the installation was successful:

```bash
python -m compas
```

In the list of extensions, you should see `compas_robots`.

## Install for Rhino

`compas_robots` is compatible with Rhino 8 and later versions.

### Rhino Script Editor

To use `compas_robots` in a Python script, simply add the requirement header to the top of your script in the Rhino 8 Script Editor:

```python
# r: compas_robots
```
