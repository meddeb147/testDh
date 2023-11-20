import 'controller/security_policy_controller.dart';
import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/core/utils/validation_functions.dart';
import 'package:aziz_s_application1/widgets/app_bar/appbar_image.dart';
import 'package:aziz_s_application1/widgets/app_bar/appbar_title.dart';
import 'package:aziz_s_application1/widgets/app_bar/custom_app_bar.dart';
import 'package:aziz_s_application1/widgets/custom_button.dart';
import 'package:aziz_s_application1/widgets/custom_text_form_field.dart';
import 'package:flutter/material.dart';

// ignore_for_file: must_be_immutable
class SecurityPolicyScreen extends GetWidget<SecurityPolicyController> {
  GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return SafeArea(
        child: Scaffold(
            resizeToAvoidBottomInset: false,
            backgroundColor: ColorConstant.gray5001,
            appBar: CustomAppBar(
                height: getVerticalSize(53),
                leadingWidth: 40,
                leading: AppbarImage(
                    height: getSize(24),
                    width: getSize(24),
                    svgPath: ImageConstant.imgArrowleft,
                    margin: getMargin(left: 16, top: 12, bottom: 17),
                    onTap: () {
                      onTapArrowleft1();
                    }),
                centerTitle: true,
                title: AppbarTitle(text: "lbl_login".tr)),
            body: Form(
                key: _formKey,
                child: Container(
                    width: double.maxFinite,
                    padding:
                        getPadding(left: 16, top: 23, right: 16, bottom: 23),
                    child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.start,
                        children: [
                          Text("msg_username_or_email".tr,
                              overflow: TextOverflow.ellipsis,
                              textAlign: TextAlign.left,
                              style: AppStyle.txtGilroyMedium16Bluegray800),
                          CustomTextFormField(
                              focusNode: FocusNode(),
                              controller: controller.emailController,
                              hintText: "msg_michellerock_gmail_com".tr,
                              margin: getMargin(top: 8),
                              textInputType: TextInputType.emailAddress,
                              validator: (value) {
                                if (value == null ||
                                    (!isValidEmail(value, isRequired: true))) {
                                  return "Please enter valid email";
                                }
                                return null;
                              }),
                          Padding(
                              padding: getPadding(top: 19),
                              child: Text("lbl_password".tr,
                                  overflow: TextOverflow.ellipsis,
                                  textAlign: TextAlign.left,
                                  style: AppStyle.txtGilroyMedium16)),
                          Obx(() => CustomTextFormField(
                              focusNode: FocusNode(),
                              controller: controller.group10198Controller,
                              hintText: "lbl_enter_password".tr,
                              margin: getMargin(top: 7),
                              padding: TextFormFieldPadding.PaddingT12,
                              textInputType: TextInputType.visiblePassword,
                              suffix: InkWell(
                                  onTap: () {
                                    controller.isShowPassword.value =
                                        !controller.isShowPassword.value;
                                  },
                                  child: Container(
                                      margin: getMargin(all: 12),
                                      child: CustomImageView(
                                          svgPath:
                                              controller.isShowPassword.value
                                                  ? ImageConstant.imgEye
                                                  : ImageConstant.imgEye))),
                              suffixConstraints: BoxConstraints(
                                  maxHeight: getVerticalSize(44)),
                              validator: (value) {
                                if (value == null ||
                                    (!isValidPassword(value,
                                        isRequired: true))) {
                                  return "Please enter valid password";
                                }
                                return null;
                              },
                              isObscureText: controller.isShowPassword.value)),
                          Padding(
                              padding: getPadding(top: 20),
                              child: Text("msg_sequrity_question".tr,
                                  overflow: TextOverflow.ellipsis,
                                  textAlign: TextAlign.left,
                                  style: AppStyle.txtGilroyMedium16)),
                          Container(
                              margin: getMargin(top: 6),
                              padding: getPadding(all: 10),
                              decoration: AppDecoration.outlineBluegray100
                                  .copyWith(
                                      borderRadius:
                                          BorderRadiusStyle.roundedBorder8),
                              child: Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  children: [
                                    Padding(
                                        padding: getPadding(
                                            left: 2, top: 3, bottom: 1),
                                        child: Text(
                                            "msg_what_was_your_first".tr,
                                            overflow: TextOverflow.ellipsis,
                                            textAlign: TextAlign.left,
                                            style: AppStyle
                                                .txtGilroyMedium16Bluegray200)),
                                    CustomImageView(
                                        svgPath: ImageConstant
                                            .imgArrowdownBlueGray600,
                                        height: getSize(24),
                                        width: getSize(24))
                                  ])),
                          Padding(
                              padding: getPadding(top: 19),
                              child: Text("lbl_answer".tr,
                                  overflow: TextOverflow.ellipsis,
                                  textAlign: TextAlign.left,
                                  style:
                                      AppStyle.txtGilroyMedium16Bluegray800)),
                          CustomTextFormField(
                              focusNode: FocusNode(),
                              controller: controller.group10198OneController,
                              hintText: "lbl_pluto".tr,
                              margin: getMargin(top: 7),
                              textInputAction: TextInputAction.done),
                          CustomButton(
                              height: getVerticalSize(50),
                              text: "lbl_sign_in2".tr,
                              margin: getMargin(top: 24, bottom: 5))
                        ])))));
  }

  onTapArrowleft1() {
    Get.back();
  }
}
