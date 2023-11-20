import 'controller/edit_profile_controller.dart';
import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/core/utils/validation_functions.dart';
import 'package:aziz_s_application1/widgets/app_bar/appbar_image.dart';
import 'package:aziz_s_application1/widgets/app_bar/appbar_title.dart';
import 'package:aziz_s_application1/widgets/app_bar/custom_app_bar.dart';
import 'package:aziz_s_application1/widgets/custom_button.dart';
import 'package:aziz_s_application1/widgets/custom_icon_button.dart';
import 'package:aziz_s_application1/widgets/custom_text_form_field.dart';
import 'package:flutter/material.dart';

// ignore_for_file: must_be_immutable
class EditProfileScreen extends GetWidget<EditProfileController> {
  GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return SafeArea(
        child: Scaffold(
            resizeToAvoidBottomInset: false,
            backgroundColor: ColorConstant.gray5001,
            appBar: CustomAppBar(
                height: getVerticalSize(48),
                leadingWidth: 40,
                leading: AppbarImage(
                    height: getSize(24),
                    width: getSize(24),
                    svgPath: ImageConstant.imgArrowleft,
                    margin: getMargin(left: 16, top: 12, bottom: 12),
                    onTap: () {
                      onTapArrowleft();
                    }),
                centerTitle: true,
                title: AppbarTitle(text: "lbl_edit_profile".tr)),
            body: Form(
                key: _formKey,
                child: Container(
                    width: double.maxFinite,
                    padding:
                        getPadding(left: 15, top: 25, right: 15, bottom: 25),
                    child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.start,
                        children: [
                          Align(
                              alignment: Alignment.center,
                              child: Container(
                                  height: getSize(150),
                                  width: getSize(150),
                                  child: Stack(
                                      alignment: Alignment.topRight,
                                      children: [
                                        CustomImageView(
                                            imagePath: ImageConstant
                                                .imgEllipse5150x150,
                                            height: getSize(150),
                                            width: getSize(150),
                                            radius: BorderRadius.circular(
                                                getHorizontalSize(75)),
                                            alignment: Alignment.center),
                                        CustomIconButton(
                                            height: 30,
                                            width: 30,
                                            margin: getMargin(top: 5, right: 2),
                                            alignment: Alignment.topRight,
                                            child: CustomImageView(
                                                svgPath:
                                                    ImageConstant.imgForward))
                                      ]))),
                          Padding(
                              padding: getPadding(left: 1, top: 26),
                              child: Text("lbl_first_name".tr,
                                  overflow: TextOverflow.ellipsis,
                                  textAlign: TextAlign.left,
                                  style: AppStyle.txtGilroyMedium16)),
                          CustomTextFormField(
                              focusNode: FocusNode(),
                              controller: controller.group10198Controller,
                              hintText: "lbl_michelle".tr,
                              margin: getMargin(left: 1, top: 8)),
                          Padding(
                              padding: getPadding(left: 1, top: 19),
                              child: Text("lbl_last_name".tr,
                                  overflow: TextOverflow.ellipsis,
                                  textAlign: TextAlign.left,
                                  style: AppStyle.txtGilroyMedium16)),
                          CustomTextFormField(
                              focusNode: FocusNode(),
                              controller: controller.group10198OneController,
                              hintText: "lbl_rock".tr,
                              margin: getMargin(left: 1, top: 7)),
                          Padding(
                              padding: getPadding(left: 1, top: 18),
                              child: Text("lbl_email_id2".tr,
                                  overflow: TextOverflow.ellipsis,
                                  textAlign: TextAlign.left,
                                  style:
                                      AppStyle.txtGilroyMedium16Bluegray800)),
                          CustomTextFormField(
                              focusNode: FocusNode(),
                              controller: controller.emailController,
                              hintText: "msg_michellerock_gmail_com".tr,
                              margin: getMargin(left: 1, top: 8),
                              textInputType: TextInputType.emailAddress,
                              validator: (value) {
                                if (value == null ||
                                    (!isValidEmail(value, isRequired: true))) {
                                  return "Please enter valid email";
                                }
                                return null;
                              }),
                          Padding(
                              padding: getPadding(left: 1, top: 18),
                              child: Text("lbl_website".tr,
                                  overflow: TextOverflow.ellipsis,
                                  textAlign: TextAlign.left,
                                  style:
                                      AppStyle.txtGilroyMedium16Bluegray800)),
                          CustomTextFormField(
                              focusNode: FocusNode(),
                              controller: controller.weburlController,
                              hintText: "msg_michellerock_com".tr,
                              margin: getMargin(left: 1, top: 8)),
                          Padding(
                              padding: getPadding(left: 1, top: 18),
                              child: Text("lbl_mobile_number".tr,
                                  overflow: TextOverflow.ellipsis,
                                  textAlign: TextAlign.left,
                                  style:
                                      AppStyle.txtGilroyMedium16Bluegray800)),
                          CustomTextFormField(
                              focusNode: FocusNode(),
                              controller: controller.mobileNoController,
                              hintText: "lbl_1_2323232323".tr,
                              margin: getMargin(left: 1, top: 8),
                              textInputAction: TextInputAction.done),
                          CustomButton(
                              height: getVerticalSize(50),
                              text: "lbl_save".tr,
                              margin: getMargin(left: 2, top: 24, bottom: 5))
                        ])))));
  }

  onTapArrowleft() {
    Get.back();
  }
}
