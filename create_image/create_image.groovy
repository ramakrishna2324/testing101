freeStyleJob('create_image') {
    logRotator(numToKeep = 100)
    label("shared")
    parameters {
      stringParam("account_number", "", "account_number")
      stringParam("role_name", "operations/jenkins-slave-jdfdevopsci", "role_name")
      stringParam("region", "us-east-1", "region")

      stringParam("image_description", "", "image_description")
      stringParam("instance_id", "", "instance_id")
      stringParam("image_name", "", "image_name")
    }
    scm {
        git {
            remote {
                url("https://githubcloud.deere.com/ManagementServices/python-scripts.git")
                credentials("GitHubCloud_Jenkins_API_Token")
            }
            branch('master')
            extensions {
                submoduleOptions {
                    recursive()
                    tracking()
                }
            }
        }
    }
    steps {
        shell('''#!/bin/bash
            python -u ec2/create_image/create_image.py \\
            --account_number $account_number \\
            --role_name $role_name \\
            --region $region \\
            --image_description $image_description \\
            --instance_id $instance_id \\
            --image_name $image_name \\
        ''')
    }
}
