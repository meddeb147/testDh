import 'controller/two_factor_authentication_controller.dart';
import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/widgets/custom_button.dart';
import 'package:flutter/material.dart';

class TwoFactorAuthenticationScreen
    extends GetWidget<TwoFactorAuthenticationController> {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
        child: Scaffold(
            backgroundColor: ColorConstant.gray5001,
            body: Container(
                width: double.maxFinite,
                padding: getPadding(left: 16, right: 16),
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CustomImageView(
                          svgPath: ImageConstant.imgMobile,
                          height: getVerticalSize(60),
                          width: getHorizontalSize(38)),
                      Padding(
                          padding: getPadding(top: 13),
                          child: Text("msg_otp_verification".tr,
                              overflow: TextOverflow.ellipsis,
                              textAlign: TextAlign.left,
                              style: AppStyle.txtGilroySemiBold24BlueA700)),
                      Padding(
                          padding: getPadding(top: 32),
                          child: RichText(
                              text: TextSpan(children: [
                                TextSpan(
                                    text: "OTP Is Send to".tr,
                                    style: TextStyle(
                                        color:
                                            ColorConstant.fromHex("#ff74839d"),
                                        fontSize: getFontSize(18),
                                        fontFamily: 'Gilroy',
                                        fontWeight: FontWeight.w500)),
                                TextSpan(
                                    text: " ",
                                    style: TextStyle(
                                        color:
                                            ColorConstant.fromHex("#ff666666"),
                                        fontSize: getFontSize(18),
                                        fontFamily: 'Gilroy',
                                        fontWeight: FontWeight.w500)),
                                TextSpan(
                                    text: "+91 01234567890".tr,
                                    style: TextStyle(
                                        color:
                                            ColorConstant.fromHex("#ff0061ff"),
                                        fontSize: getFontSize(18),
                                        fontFamily: 'Gilroy',
                                        fontWeight: FontWeight.w700))
                              ]),
                              textAlign: TextAlign.left)),
                      CustomImageView(
                          svgPath: ImageConstant.imgFrame9880,
                          height: getVerticalSize(52),
                          width: getHorizontalSize(320),
                          margin: getMargin(top: 27)),
                      CustomButton(
                          height: getVerticalSize(50),
                          text: "lbl_verify_otp".tr,
                          margin: getMargin(top: 32)),
                      Padding(
                          padding: getPadding(top: 26, bottom: 5),
                          child: RichText(
                              text: TextSpan(children: [
                                TextSpan(
                                    text: "Didn’t Recieved Code ?".tr,
                                    style: TextStyle(
                                        color:
                                            ColorConstant.fromHex("#ff74839d"),
                                        fontSize: getFontSize(16),
                                        fontFamily: 'Gilroy',
                                        fontWeight: FontWeight.w500)),
                                TextSpan(
                                    text: " ",
                                    style: TextStyle(
                                        color:
                                            ColorConstant.fromHex("#ff0061ff"),
                                        fontSize: getFontSize(16),
                                        fontFamily: 'Gilroy',
                                        fontWeight: FontWeight.w500)),
                                TextSpan(
                                    text: "Resend ".tr,
                                    style: TextStyle(
                                        color:
                                            ColorConstant.fromHex("#ff0061ff"),
                                        fontSize: getFontSize(16),
                                        fontFamily: 'Gilroy',
                                        fontWeight: FontWeight.w700))
                              ]),
                              textAlign: TextAlign.left))
                    ]))));
  }
}
