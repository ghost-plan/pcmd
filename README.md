## Setuptools / Wheel/ Twine Build Tool

Package Source Code

- pip3 install setuptools ; pip3 install wheel
- python3 setup.py sdist bdist_wheel

Upload Package

- pip3 install twine
- twine upload dist/*

## Poetry Build Tool

- Activating the virtual environment:poetry shell
- add deps:poetry add xxx (poetry add `cat requirements.txt`) or poetry install
- poetry build | pip3 install dist/padb-1.2.0-py3-none-any.whl --force
- 开发调试：  poetry build | poetry run python src/main.py --help
- 发布：poetry build  | poetry publish

## Reference:

[awesome adb](http://adbcommand.com/awesome-adb/cn)

[Android】ADB工具原理探究](https://itimetraveler.github.io/2019/06/07/Android%20ADB%E5%8E%9F%E7%90%86%E6%8E%A2%E7%A9%B6/#ADB%E7%AE%80%E4%BB%8B)

[python代码规范](https://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/python_style_rules/)

[poetry-monorepo](https://gitlab.com/gerbenoostra/poetry-monorepo/-/tree/main/)

[python-monorepo](https://github.com/ya-mori/python-monorepo)

[tweag / python-monorepo-example](https://github.com/tweag/python-monorepo-example/blob/main/templates/pylibrary/pyproject.toml)

[Python 项目工程化开发指南](https://pyloong.github.io/pythonic-project-guidelines/practices/web/#23)

[poetry](https://python-poetry.org/docs/repositories/)
