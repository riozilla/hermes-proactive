# Contributing

Keep changes generic, evidence-based, and easy to adapt to different Hermes installations. Do not add a real profile, local schedule, contact, endpoint, account, secret, conversation excerpt, or private incident to an example or test. Use synthetic data and reserved example domains.

Preserve the distinction between proposed behavior and implemented runtime support. Cite primary documentation for version-sensitive integration claims. Do not redistribute third-party prompt dumps or vendor materials under this project's license.

When changing jobs, update the canonical job sections, complete per-job prompts, planning file, documentation, and generated playbook together. Run:

```bash
python3 scripts/build_playbook.py
python3 scripts/validate_repo.py
python3 scripts/check_public_content.py
python3 -m unittest discover -s tests -v
```

Run the public-content check before committing or pushing. Keep local forbidden-term lists outside the checkout. Never add private terms to a public allowlist or test failure to make CI pass. Describe untested behavior honestly.

Use a pull request with the intent, changed behavior, tests run, and any remaining limitations. Do not include private runtime logs as evidence.
