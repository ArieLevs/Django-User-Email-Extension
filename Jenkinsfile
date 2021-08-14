@Library('jenkins-shared-library@master')

import nalkinscloud.shared_functions

def Functions = new shared_functions()

def label = "trigger-${UUID.randomUUID().toString()}"
podTemplate(label: label,
        containers: [
                containerTemplate(
                        name: 'jnlp',
                        image: 'jenkinsci/jnlp-slave:alpine',
                        ttyEnabled: true
                )
        ]
) {
    node(label) {
        try {
            timeout(time: 10, unit: 'MINUTES') {
                ansiColor('xterm') {
                    container('jnlp') {
                        stage("Call main pipeline") {
                            String projectName = env.JOB_NAME.toString().split('/')[1]
                            if (env.CHANGE_ID && env.CHANGE_BRANCH) {
                                Functions.mainPythonCITrigger("$projectName", "${env.BRANCH_NAME}", "${env.CHANGE_ID}", "${env.CHANGE_BRANCH}")
                            } else {
                                Functions.mainPythonCITrigger("$projectName", "${BRANCH_NAME}")
                            }
                        }
                    }
                }
            }
        } catch (exception) {
            currentBuild.result = 'FAILURE'
            println(exception)
        } finally {
            def currentResult = currentBuild.result
            if (currentResult == 'SUCCESS') {
                println("SUCCESS")
            } else {
                println("FAILURE")
            }
        }
    }
}
