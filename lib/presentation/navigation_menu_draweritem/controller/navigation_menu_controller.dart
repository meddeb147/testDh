import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/presentation/navigation_menu_draweritem/models/navigation_menu_model.dart';
import 'package:flutter/material.dart';

class NavigationMenuController extends GetxController {
  TextEditingController toggleController = TextEditingController();

  Rx<NavigationMenuModel> navigationMenuModelObj = NavigationMenuModel().obs;

  @override
  void onReady() {
    super.onReady();
  }

  @override
  void onClose() {
    super.onClose();
    toggleController.dispose();
  }
}
