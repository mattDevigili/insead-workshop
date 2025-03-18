# Cloud Computing for Research

![tux](.viz/_.png)

## Topics

1. [EC2 instance](https://eu-north-1.console.aws.amazon.com/ec2/home?region=eu-north-1#Overview:)
2. [AWS pricing](https://calculator.aws/#/)
3. Minimum viable instance for this workshop `t3.large`
4. Access via EC2 Instance Connect
5. Config with VSCode:
```{bash}
Host aws-ec2
  HostName ec2-****.eu-north-1.compute.amazonaws.com
  User ubuntu
  IdentityFile /YOUR/PATH/TO/key.pem
```
6. set-up:
    - run: `git clone https://github.com/mattDevigili/insead-workshop.git`
    - set-up vscode extensions (python, jupyter, mongodb, live server)
    - run `bash set_up`
7. have fun!

## Repo Structure

```
.
├── requirements.txt # python requirements
├── set_up.sh # bash script
├── step-0    # scraping
├── step-1    # storing
├── step-2    # processing
└── step-3    # simple stats
```