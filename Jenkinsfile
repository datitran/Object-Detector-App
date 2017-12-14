#!/usr/bin/env groovy

pipeline {

    /* Create instance (Agent) to run Jenkins pipeline on

    Section creates a docker container with anaconda installed on it for jenkins pipeline to run on. Arguments work
    as follows:
        `-u 0` user ID, which has root value. Good reference about docker UID/GIDs (https://goo.gl/bYFxVh)
        `--rm` If a docker container with the same name already exists, remove it
        `--name ai-conda` Give this docker instance the name `ai-conda`
        `-v _:_` map volumes. Specifically, map `passwd`, `group` and the conda packages volumes to the container
    */
    agent {
        docker {
            image 'continuumio/miniconda3'
            args '-u 0 --rm --name ai-conda -v /etc/passwd:/etc/passwd -v /etc/group:/etc/group -v /home/jenkins/.conda3/pkgs:/home/jenkins/.conda/pkgs:rw,z'
        }
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            environment {
                CONDA_ENV = "${env.WORKSPACE}/test/${env.STAGE_NAME}"
            }
            steps {
                /* Recreate a conda environment from the config file

                    `-q` quite mode. Remove to see verbose output
                    `--force` remove previously existing environment of the same name
                    `-f FILE` environment definition file
                    `-p PATH` Full path to environment prefix (replacing default)
                 */
                sh 'conda env create -q --force -f environment.yml -p $CONDA_ENV'

                /*  Activate the environment and run unit tests

                    `source ...` activate the environment
                    `python -m pytest` run `pytest` as a module
                    `python -m unittest...` run `unittest` on the `object_detection` directory, pattern matching all of
                        the files that end in `_test.py`

                 */
                sh '''#!/bin/bash -ex
                    source $CONDA_ENV/bin/activate $CONDA_ENV
                    python -m pytest
                    python -m unittest discover -s object_detection -p "*_test.py"
                '''

            }
        }

        /*
        stage('Deploy - Staging'){
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                echo 'Placeholder: Deploying to staging/dev'
            }
        }

        stage('Sanity check') {
            steps {
                input "Does the staging env look good? Good enough to deploy into production?"
            }
        }

        stage('Deploy - Production') {
            steps {
                echo 'Placeholder: Deploying to prod'
            }
        }
        */
    }

    /* TODO(Alex): Fix Slack Notifications. */
    post {
        always {
            echo 'The job has finished.'
            slackSend channel: '#ai-nsf-jenkins-jobs',
                color: 'good',
                message: "The pipeline ${currentBuild.fillDisplayName} completed."
        }
        success {
            slackSend channel: '#ai-nsf-jenkins-jobs',
                color: 'good',
                message: "The pipeline ${currentBuild.fillDisplayName} completed successfully."
        }
        unstable {
            slackSend channel: '#ai-nsf-jenkins-jobs',
                color: 'warning',
                message: "The pipeline ${currentBuild.fillDisplayName} is unstable. Check it out here: ${env.BUILD_URL}"
        }
        failure {
            slackSend channel: '#ai-nsf-jenkins-jobs',
                color: 'danger',
                message: "@all The pipeline ${currentBuild.fillDisplayName} has failed! Check it out here: ${env.BUILD_URL}"
        }
        /*
        changed {

        }
        */
    }
}