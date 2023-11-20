import 'controller/password_encryption_controller.dart';
import 'package:aziz_s_application1/core/app_export.dart';
import 'package:flutter/material.dart';

// ignore_for_file: must_be_immutable
class PasswordEncryptionScreen extends GetWidget<PasswordEncryptionController> {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Scaffold(
        backgroundColor: ColorConstant.gray5001,
        body: Container(
          width: double.maxFinite,
          padding: getPadding(
            top: 279,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              CustomImageView(
                svgPath: ImageConstant.imgCheckmark66x54,
                height: getVerticalSize(
                  66,
                ),
                width: getHorizontalSize(
                  54,
                ),
              ),
              Padding(
                padding: getPadding(
                  top: 30,
                ),
                child: Text(
                  "msg_password_encryption".tr,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.left,
                  style: AppStyle.txtGilroySemiBold24,
                ),
              ),
              Container(
                width: getHorizontalSize(
                  221,
                ),
                margin: getMargin(
                  top: 21,
                  bottom: 5,
                ),
                child: Text(
                  "msg_we_ve_protectected".tr,
                  maxLines: null,
                  textAlign: TextAlign.center,
                  style: AppStyle.txtGilroyMedium16Bluegray400,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
