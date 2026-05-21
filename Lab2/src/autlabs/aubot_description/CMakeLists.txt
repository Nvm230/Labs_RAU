cmake_minimum_required(VERSION 3.5)
project(aubot_description)

find_package(ament_cmake REQUIRED)

# Install URDF, launch, rviz, models, worlds
install(DIRECTORY urdf launch rviz models worlds
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
