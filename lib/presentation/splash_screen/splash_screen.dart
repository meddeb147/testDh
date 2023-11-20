import 'controller/splash_controller.dart';
import 'package:aziz_s_application1/core/app_export.dart';
import 'package:flutter/material.dart';

// ignore_for_file: must_be_immutable
class SplashScreen extends GetWidget<SplashController> {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Scaffold(
        backgroundColor: ColorConstant.gray5001,
        body: Container(
          width: double.maxFinite,
          padding: getPadding(
            left: 33,
            right: 33,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CustomImageView(
                svgPath: ImageConstant.imgVectorBlueA70034x360,
                height: getVerticalSize(
                  34,
                ),
                width: getHorizontalSize(
                  360,
                ),
                margin: getMargin(
                  bottom: 5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
