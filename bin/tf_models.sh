#!/usr/bin/env bash


CURR_DIR=$(pwd)
SITE_PACK=$(python -c "import site; print(site.getsitepackages()[0])")
MODELS_DEST=$SITE_PACK/tensorflow/models


cd $MODELS_DEST || mkdir $MODELS_DEST && cd $MODELS_DEST


# Spare Checkout of tensorflow models repo
inside_git_repo="$(git rev-parse --is-inside-work-tree 2>/dev/null)"
if ! $inside_git_repo;
then
    git init \
     && git remote add origin https://github.com/tensorflow/models.git \
     && git config core.sparsecheckout true \
     && echo "research/slim/*" >> .git/info/sparse-checkout \
     && git pull --depth=1 origin master
fi

# get slim directory, set it to python path
# TODO(Alex) Set PYTHONPATH env variable, don't just set sys.path
python -c "import sys; sys.exit(-1) if not list(filter(lambda x: 'research/slim' in x, sys.path)) else sys.exit(0)" \
  || cd research/slim \
  && SLIM_DIR=$(pwd) \
  && python -c "import sys; sys.path.append('$SLIM_DIR')" \
  && echo "Added slim to python path"

# Return to original dir
cd $CURR_DIR
