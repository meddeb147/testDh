import 'controller/navigation_menu_controller.dart';
import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/widgets/custom_button.dart';
import 'package:aziz_s_application1/widgets/custom_text_form_field.dart';
import 'package:flutter/material.dart';

class NavigationMenuDraweritem extends StatelessWidget {
  NavigationMenuDraweritem(this.controller);

  NavigationMenuController controller;

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: Container(
        width: getHorizontalSize(
          310,
        ),
        padding: getPadding(
          all: 24,
        ),
        decoration: AppDecoration.fillGray50,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            Padding(
              padding: getPadding(
                right: 62,
              ),
              child: Row(
                children: [
                  CustomImageView(
                    imagePath: ImageConstant.img8148x48,
                    height: getSize(
                      48,
                    ),
                    width: getSize(
                      48,
                    ),
                    radius: BorderRadius.circular(
                      getHorizontalSize(
                        24,
                      ),
                    ),
                  ),
                  Container(
                    width: getHorizontalSize(
                      139,
                    ),
                    margin: getMargin(
                      left: 12,
                      top: 4,
                      bottom: 2,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.start,
                      children: [
                        Text(
                          "lbl_ashfak_sayem".tr,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.left,
                          style: AppStyle.txtGilroySemiBold16,
                        ),
                        Padding(
                          padding: getPadding(
                            top: 5,
                          ),
                          child: Text(
                            "msg_ashfaksayem_gmail_com".tr,
                            overflow: TextOverflow.ellipsis,
                            textAlign: TextAlign.left,
                            style: AppStyle.txtGilroyMedium12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            Container(
              margin: getMargin(
                top: 32,
              ),
              padding: getPadding(
                left: 12,
                top: 13,
                right: 12,
                bottom: 13,
              ),
              decoration: AppDecoration.fillBlueA700.copyWith(
                borderRadius: BorderRadiusStyle.roundedBorder8,
              ),
              child: Row(
                children: [
                  CustomImageView(
                    svgPath: ImageConstant.imgCalendar,
                    height: getSize(
                      24,
                    ),
                    width: getSize(
                      24,
                    ),
                  ),
                  Padding(
                    padding: getPadding(
                      left: 6,
                      top: 1,
                      bottom: 2,
                    ),
                    child: Text(
                      "lbl_calendar".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtGilroySemiBold16WhiteA700,
                    ),
                  ),
                  Spacer(),
                  CustomButton(
                    height: getVerticalSize(
                      20,
                    ),
                    width: getSize(
                      20,
                    ),
                    text: "lbl_2".tr,
                    margin: getMargin(
                      top: 2,
                      bottom: 2,
                    ),
                    variant: ButtonVariant.FillLightblue100,
                    padding: ButtonPadding.PaddingAll3,
                    fontStyle: ButtonFontStyle.InterSemiBold10,
                  ),
                ],
              ),
            ),
            Align(
              alignment: Alignment.center,
              child: Padding(
                padding: getPadding(
                  left: 12,
                  top: 21,
                  right: 12,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CustomImageView(
                      svgPath: ImageConstant.imgLock24x24,
                      height: getSize(
                        24,
                      ),
                      width: getSize(
                        24,
                      ),
                    ),
                    Padding(
                      padding: getPadding(
                        left: 6,
                        top: 1,
                        bottom: 2,
                      ),
                      child: Text(
                        "lbl_rewards".tr,
                        overflow: TextOverflow.ellipsis,
                        textAlign: TextAlign.left,
                        style: AppStyle.txtGilroySemiBold16Bluegray700,
                      ),
                    ),
                    Spacer(),
                    CustomButton(
                      height: getVerticalSize(
                        20,
                      ),
                      width: getSize(
                        20,
                      ),
                      text: "lbl_2".tr,
                      margin: getMargin(
                        top: 2,
                        bottom: 2,
                      ),
                      variant: ButtonVariant.FillRed200,
                      padding: ButtonPadding.PaddingAll3,
                      fontStyle: ButtonFontStyle.InterSemiBold10,
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: getPadding(
                left: 12,
                top: 34,
              ),
              child: Row(
                children: [
                  CustomImageView(
                    svgPath: ImageConstant.imgLocation,
                    height: getSize(
                      24,
                    ),
                    width: getSize(
                      24,
                    ),
                  ),
                  Padding(
                    padding: getPadding(
                      left: 6,
                      top: 1,
                      bottom: 2,
                    ),
                    child: Text(
                      "lbl_address".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtGilroySemiBold16Bluegray700,
                    ),
                  ),
                ],
              ),
            ),
            Padding(
              padding: getPadding(
                left: 12,
                top: 34,
              ),
              child: Row(
                children: [
                  CustomImageView(
                    svgPath: ImageConstant.imgCalendar24x24,
                    height: getSize(
                      24,
                    ),
                    width: getSize(
                      24,
                    ),
                  ),
                  Padding(
                    padding: getPadding(
                      left: 6,
                      top: 3,
                    ),
                    child: Text(
                      "msg_payments_methods".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtGilroySemiBold16Bluegray700,
                    ),
                  ),
                ],
              ),
            ),
            Align(
              alignment: Alignment.center,
              child: Padding(
                padding: getPadding(
                  left: 12,
                  top: 34,
                  right: 12,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CustomImageView(
                      svgPath: ImageConstant.imgSettings1,
                      height: getSize(
                        24,
                      ),
                      width: getSize(
                        24,
                      ),
                    ),
                    Padding(
                      padding: getPadding(
                        left: 6,
                        top: 1,
                        bottom: 2,
                      ),
                      child: Text(
                        "lbl_offers".tr,
                        overflow: TextOverflow.ellipsis,
                        textAlign: TextAlign.left,
                        style: AppStyle.txtGilroySemiBold16Bluegray700,
                      ),
                    ),
                    Spacer(),
                    CustomButton(
                      height: getVerticalSize(
                        20,
                      ),
                      width: getSize(
                        20,
                      ),
                      text: "lbl_2".tr,
                      margin: getMargin(
                        top: 2,
                        bottom: 2,
                      ),
                      variant: ButtonVariant.FillGreenA100,
                      padding: ButtonPadding.PaddingAll3,
                      fontStyle: ButtonFontStyle.InterSemiBold10,
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: getPadding(
                left: 12,
                top: 34,
              ),
              child: Row(
                children: [
                  CustomImageView(
                    svgPath: ImageConstant.imgUser24x24,
                    height: getSize(
                      24,
                    ),
                    width: getSize(
                      24,
                    ),
                  ),
                  Padding(
                    padding: getPadding(
                      left: 6,
                      top: 1,
                      bottom: 2,
                    ),
                    child: Text(
                      "lbl_refer_a_friend".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtGilroySemiBold16Bluegray700,
                    ),
                  ),
                ],
              ),
            ),
            Padding(
              padding: getPadding(
                left: 12,
                top: 34,
              ),
              child: Row(
                children: [
                  CustomImageView(
                    svgPath: ImageConstant.imgCall,
                    height: getSize(
                      24,
                    ),
                    width: getSize(
                      24,
                    ),
                  ),
                  Padding(
                    padding: getPadding(
                      left: 6,
                      top: 2,
                      bottom: 1,
                    ),
                    child: Text(
                      "lbl_support".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtGilroySemiBold16Bluegray700,
                    ),
                  ),
                ],
              ),
            ),
            Spacer(),
            Divider(
              height: getVerticalSize(
                2,
              ),
              thickness: getVerticalSize(
                2,
              ),
              color: ColorConstant.blueGray1006c,
            ),
            Padding(
              padding: getPadding(
                left: 12,
                top: 13,
              ),
              child: Row(
                children: [
                  CustomImageView(
                    svgPath: ImageConstant.imgQuestion24x24,
                    height: getSize(
                      24,
                    ),
                    width: getSize(
                      24,
                    ),
                  ),
                  Padding(
                    padding: getPadding(
                      left: 6,
                      top: 1,
                      bottom: 2,
                    ),
                    child: Text(
                      "lbl_colour_scheme".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtGilroySemiBold16Bluegray700,
                    ),
                  ),
                ],
              ),
            ),
            Container(
              margin: getMargin(
                top: 21,
                bottom: 24,
              ),
              padding: getPadding(
                all: 4,
              ),
              decoration: AppDecoration.fillGray200.copyWith(
                borderRadius: BorderRadiusStyle.circleBorder20,
              ),
              child: Row(
                children: [
                  CustomTextFormField(
                    width: getHorizontalSize(
                      125,
                    ),
                    focusNode: FocusNode(),
                    controller: controller.toggleController,
                    hintText: "lbl_light".tr,
                    variant: TextFormFieldVariant.OutlineBlack9003f,
                    shape: TextFormFieldShape.CircleBorder16,
                    padding: TextFormFieldPadding.PaddingT6,
                    fontStyle: TextFormFieldFontStyle.GilroySemiBold14,
                    textInputAction: TextInputAction.done,
                    prefix: Container(
                      margin: getMargin(
                        left: 26,
                        top: 4,
                        right: 8,
                        bottom: 4,
                      ),
                      child: CustomImageView(
                        svgPath: ImageConstant.imgBrightness,
                      ),
                    ),
                    prefixConstraints: BoxConstraints(
                      maxHeight: getVerticalSize(
                        32,
                      ),
                    ),
                  ),
                  CustomImageView(
                    svgPath: ImageConstant.imgUiiconmoonlight,
                    height: getSize(
                      24,
                    ),
                    width: getSize(
                      24,
                    ),
                    margin: getMargin(
                      left: 31,
                      top: 4,
                      bottom: 4,
                    ),
                  ),
                  Padding(
                    padding: getPadding(
                      left: 8,
                      top: 7,
                      right: 35,
                      bottom: 7,
                    ),
                    child: Text(
                      "lbl_dark".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtGilroySemiBold14,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
