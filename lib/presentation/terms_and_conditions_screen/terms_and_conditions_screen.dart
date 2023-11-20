import 'controller/terms_and_conditions_controller.dart';
import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/widgets/app_bar/appbar_image.dart';
import 'package:aziz_s_application1/widgets/app_bar/appbar_title.dart';
import 'package:aziz_s_application1/widgets/app_bar/custom_app_bar.dart';
import 'package:flutter/material.dart';

class TermsAndConditionsScreen extends GetWidget<TermsAndConditionsController> {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
        child: Scaffold(
            backgroundColor: ColorConstant.gray5001,
            appBar: CustomAppBar(
                height: getVerticalSize(51),
                leadingWidth: 40,
                leading: AppbarImage(
                    height: getSize(24),
                    width: getSize(24),
                    svgPath: ImageConstant.imgArrowleft,
                    margin: getMargin(left: 16, top: 14, bottom: 13),
                    onTap: () {
                      onTapArrowleft4();
                    }),
                centerTitle: true,
                title: AppbarTitle(text: "msg_terms_and_conditions".tr)),
            body: Container(
                width: double.maxFinite,
                padding: getPadding(left: 16, top: 28, right: 16, bottom: 28),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      Text("lbl_lorem_ipsum".tr,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.left,
                          style: AppStyle.txtGilroySemiBold18
                              .copyWith(decoration: TextDecoration.underline)),
                      Container(
                          width: getHorizontalSize(394),
                          margin: getMargin(top: 12),
                          child: Text("msg_lorem_ipsum_dolor".tr,
                              maxLines: null,
                              textAlign: TextAlign.left,
                              style: AppStyle.txtGilroyMedium16Bluegray400)),
                      Padding(
                          padding: getPadding(top: 16),
                          child: Divider(
                              height: getVerticalSize(1),
                              thickness: getVerticalSize(1),
                              color: ColorConstant.blueGray100)),
                      Padding(
                          padding: getPadding(top: 20),
                          child: Text("lbl_lorem_ipsum".tr,
                              overflow: TextOverflow.ellipsis,
                              textAlign: TextAlign.left,
                              style: AppStyle.txtGilroySemiBold18.copyWith(
                                  decoration: TextDecoration.underline))),
                      Container(
                          width: getHorizontalSize(394),
                          margin: getMargin(top: 12),
                          child: Text("msg_lorem_ipsum_dolor".tr,
                              maxLines: null,
                              textAlign: TextAlign.left,
                              style: AppStyle.txtGilroyMedium16Bluegray400)),
                      Padding(
                          padding: getPadding(top: 16),
                          child: Divider(
                              height: getVerticalSize(1),
                              thickness: getVerticalSize(1),
                              color: ColorConstant.blueGray100)),
                      Padding(
                          padding: getPadding(top: 20),
                          child: Text("lbl_lorem_ipsum".tr,
                              overflow: TextOverflow.ellipsis,
                              textAlign: TextAlign.left,
                              style: AppStyle.txtGilroySemiBold18.copyWith(
                                  decoration: TextDecoration.underline))),
                      Container(
                          width: getHorizontalSize(394),
                          margin: getMargin(top: 12),
                          child: Text("msg_lorem_ipsum_dolor".tr,
                              maxLines: null,
                              textAlign: TextAlign.left,
                              style: AppStyle.txtGilroyMedium16Bluegray400)),
                      Padding(
                          padding: getPadding(top: 16),
                          child: Divider(
                              height: getVerticalSize(1),
                              thickness: getVerticalSize(1),
                              color: ColorConstant.blueGray100)),
                      Padding(
                          padding: getPadding(top: 20),
                          child: Text("lbl_lorem_ipsum".tr,
                              overflow: TextOverflow.ellipsis,
                              textAlign: TextAlign.left,
                              style: AppStyle.txtGilroySemiBold18.copyWith(
                                  decoration: TextDecoration.underline))),
                      Container(
                          width: getHorizontalSize(394),
                          margin: getMargin(top: 12, bottom: 5),
                          child: Text("msg_lorem_ipsum_dolor".tr,
                              maxLines: null,
                              textAlign: TextAlign.left,
                              style: AppStyle.txtGilroyMedium16Bluegray400))
                    ]))));
  }

  onTapArrowleft4() {
    Get.back();
  }
}
