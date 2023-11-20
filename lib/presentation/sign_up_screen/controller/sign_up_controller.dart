import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/presentation/sign_up_screen/models/sign_up_model.dart';
import 'package:flutter/material.dart';

class SignUpController extends GetxController {
  TextEditingController group10198Controller = TextEditingController();

  TextEditingController group10198OneController = TextEditingController();

  TextEditingController group10198TwoController = TextEditingController();

  TextEditingController group10198ThreeController = TextEditingController();

  TextEditingController group10198FourController = TextEditingController();

  Rx<SignUpModel> signUpModelObj = SignUpModel().obs;

  Rx<bool> isShowPassword = true.obs;

  @override
  void onReady() {
    super.onReady();
  }

  @override
  void onClose() {
    super.onClose();
    group10198Controller.dispose();
    group10198OneController.dispose();
    group10198TwoController.dispose();
    group10198ThreeController.dispose();
    group10198FourController.dispose();
  }
}
