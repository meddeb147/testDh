import 'controller/phone_verification_controller.dart';
import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/widgets/custom_button.dart';
import 'package:flutter/material.dart';

// ignore_for_file: must_be_immutable
class PhoneVerificationScreen extends GetWidget<PhoneVerificationController> {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Scaffold(
        backgroundColor: ColorConstant.gray5001,
        body: Container(
          width: double.maxFinite,
          padding: getPadding(
            left: 16,
            top: 76,
            right: 16,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              CustomImageView(
                svgPath: ImageConstant.imgMobile,
                height: getVerticalSize(
                  82,
                ),
                width: getHorizontalSize(
                  51,
                ),
              ),
              Padding(
                padding: getPadding(
                  top: 29,
                ),
                child: Text(
                  "msg_phone_verification".tr,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.left,
                  style: AppStyle.txtGilroySemiBold24,
                ),
              ),
              Container(
                width: getHorizontalSize(
                  302,
                ),
                margin: getMargin(
                  left: 46,
                  top: 19,
                  right: 46,
                ),
                child: Text(
                  "msg_a_text_message_with".tr,
                  maxLines: null,
                  textAlign: TextAlign.center,
                  style: AppStyle.txtGilroyMedium16Bluegray400,
                ),
              ),
              CustomImageView(
                svgPath: ImageConstant.imgGroup2507,
                height: getVerticalSize(
                  1,
                ),
                width: getHorizontalSize(
                  280,
                ),
                margin: getMargin(
                  top: 60,
                ),
              ),
              CustomButton(
                height: getVerticalSize(
                  50,
                ),
                text: "lbl_next".tr,
                margin: getMargin(
                  top: 40,
                ),
              ),
              Align(
                alignment: Alignment.centerLeft,
                child: Padding(
                  padding: getPadding(
                    top: 18,
                    bottom: 5,
                  ),
                  child: Row(
                    children: [
                      Padding(
                        padding: getPadding(
                          top: 2,
                        ),
                        child: Text(
                          "msg_didn_t_get_the_code".tr,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.left,
                          style: AppStyle.txtGilroyMedium16Bluegray400,
                        ),
                      ),
                      Padding(
                        padding: getPadding(
                          left: 12,
                          bottom: 1,
                        ),
                        child: Text(
                          "lbl_resend".tr,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.left,
                          style: AppStyle.txtGilroySemiBold16BlueA700,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
