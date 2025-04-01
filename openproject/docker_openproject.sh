docker run -d -p 8080:80 --name openproject \
  -e OPENPROJECT_HOST__NAME=localhost \
  -e OPENPROJECT_SECRET_KEY_BASE=Micr0osofttAltern9tiv3eSolutionn \
  -e OPENPROJECT_HTTPS=false \
  -v $HOME/Workspace/Docker/OpenProject/pgdata:/var/openproject/pgdata \
  -v $HOME/Workspace/Docker/OpenProject/assets:/var/openproject/assets \
  openproject/community:12

