check:
	ruff check .
	black --check .

fix:
	ruff check . --fix
	black .

status:
	git status

diff:
	git diff

test:
	pytest

coverage:
	pytest --cov=.

typecheck:
	mypy .

all-tests:
	make check
	make fix
	make test
	make diff
	make status