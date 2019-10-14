set USE_SDL2=1
set USE_GSTREAMER=1
python -m pip install --upgrade --user pip wheel setuptools pygame pygments docutils pillow
python -m pip install Cython==0.29.10 docutils pygments pypiwin32 kivy_deps.sdl2 kivy_deps.glew kivy_deps.gstreamer kivy_deps.glew_dev kivy_deps.sdl2_dev kivy_deps.gstreamer_dev
cd %~dp0\..\
IF EXIST kivy\ (
    cd kivy\
) ELSE (
    git clone git://github.com/kivy/kivy.git
    cd kivy\
)
python -m pip install .

