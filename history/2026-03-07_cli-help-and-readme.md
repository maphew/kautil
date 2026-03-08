# 2026-03-08: CLI Help and README Update

## Context

User requested that `uv run kautil --help` should show subcommand help (complete, like `kautil fingerprint --help` shows) and also be documented in README.

## Findings

1. **Initial exploration**: The CLI is built with Click, has two subcommands: `fingerprint` and `info`

2. **Multiple approaches tried**:
   - First attempt: Used `invoke_without_command=True` with callback checking `ctx.invoked_subcommand is None` - didn't work because Click intercepts --help before callback runs
   - Second attempt: Added `context_settings={"help_option_names": []}` to disable built-in help - this broke subcommand help (they showed the group help instead)
   - Third attempt: Added custom `@click.option("--help", is_flag=True, ...)` without the context_settings - initially had syntax error with invalid `add_help_option` in context_settings
   - Final working solution: Removed the problematic context_settings, just added custom --help option that triggers full help display

3. **Root cause**: Click's built-in --help handling runs before the group callback, so checking `ctx.invoked_subcommand is None` doesn't catch --help. The solution was to add a custom --help option that bypasses Click's default behavior.

4. **Technical details**:
   - Used `click.Context(cmd, info_name=name)` to create fresh contexts for each subcommand when generating their help
   - Added `or help` condition to check both no-subcommand and --help flag cases

5. **README updates**: Added full help output and references to sample files (samples/test_fingerprint.json and samples/test_fingerprint.png)

6. **Tests**: All 21 tests passed

7. **Minor fix needed**: README had an incorrect image path (`A:\dev\kautil\samples/test_fingerprint.png`) that needed to be fixed to relative path

## Result

- `kautil --help` now shows complete subcommand help including all options
- README updated with full documentation
- Changes committed and pushed to remote
