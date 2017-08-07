FROM ubuntu:14.04
RUN apt-get update --fix-missing
RUN apt-get install --yes --no-install-recommends software-properties-common
RUN apt-get install --yes --no-install-recommends curl
RUN apt-get install --yes --no-install-recommends python-pip
RUN apt-get install --yes --no-install-recommends build-essential autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus python-qt4 python-qt4-gl libgle3 python-dev
RUN apt-get install --yes --no-install-recommends python-dev libssl-dev libffi-dev
RUN pip install -U pyopenssl==0.13.1 pyasn1 ndg-httpsclient
RUN pip install flask
ADD . /code
ENTRYPOINT ["/bin/bash", "-c", "python /code/pricingsvc.py"]
