from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Receipe, Ingredients,MealPlanner

class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password=forms.CharField(label='Password',widget=forms.PasswordInput)
    password2=forms.CharField(label='Reapeat Password',widget=forms.PasswordInput)
    class Meta :
        model=User
        fields=('username','first_name','last_name','email')
    def clean_password2(self):
        cd =self.cleaned_data
        if cd['password']!=cd['password2']:
            raise forms.ValidationError('Password don\'t match')
        return cd['password2']

from django import forms
from django.forms.models import inlineformset_factory
# Assuming Receipe and Ingredients models are correctly imported

class ReceipeForm(forms.ModelForm):
    class Meta:
        model = Receipe
        fields = ['receipe_name', 'receipe_description', 'receipe_type', 'receipe_image']
        widgets = {
            # Receipe Name
            'receipe_name': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-300 rounded-xl dark:placeholder-gray-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 focus:border-orange-500 dark:focus:border-orange-400 focus:ring-2 focus:ring-orange-200 focus:outline-none transition duration-200'
            }),
            # Receipe Description
            'receipe_description': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-300 rounded-xl dark:placeholder-gray-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 focus:border-orange-500 dark:focus:border-orange-400 focus:ring-2 focus:ring-orange-200 focus:outline-none transition duration-200',
                'rows': 4
            }),
            # Receipe Type (Select)
            'receipe_type': forms.Select(attrs={
                # Note: Changed to w-full for better form flow and added shadow
                'class': 'block w-full px-4 py-3 text-gray-800 bg-gray-50 border border-gray-300 rounded-xl dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 focus:outline-none transition duration-200 shadow-sm'
            }),
            # Receipe Image
            'receipe_image': forms.ClearableFileInput(attrs={
                # Using modern file input styling
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-xl cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 p-3 transition duration-200'
            }),
        }

IngredientFormSet = inlineformset_factory(
    Receipe,
    Ingredients,
    fields=('ingredients_name',),
    widgets={
        # Ingredients Name (TextInput)
        'ingredients_name': forms.TextInput(attrs={
            # Consistent styling with other text inputs
            'class': 'block w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-300 rounded-xl dark:placeholder-gray-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 focus:border-orange-500 dark:focus:border-orange-400 focus:ring-2 focus:ring-orange-200 focus:outline-none transition duration-200'
        }),
    },
    extra=1,
    can_delete=True,
)


class MealPlannerForm(forms.ModelForm):
    class Meta:
        model = MealPlanner
        fields = ['recipe', 'meal_date', 'meal_time', 'meal_type', 'notes']
        widgets = {
            # Recipe (Select) - Wide, rounded, and uses accent focus
            'recipe': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 text-gray-800 bg-gray-50 border border-gray-300 rounded-xl dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 focus:outline-none transition duration-200 shadow-sm'
            }),
            
            # Meal Date (DateInput) - Wide, rounded, and type="date"
            'meal_date': forms.DateInput(attrs={
                'type': 'date',  
                'class': 'block w-full px-4 py-3 text-gray-800 bg-gray-50 border border-gray-300 rounded-xl dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 focus:outline-none transition duration-200'
            }),
            
            # Meal Time (TimeInput) - Wide, rounded, and type="time"
            'meal_time': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'block w-full px-4 py-3 text-gray-800 bg-gray-50 border border-gray-300 rounded-xl dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 focus:outline-none transition duration-200'
            }),
            
            # Meal Type (Select) - Wide, rounded, and uses accent focus
            'meal_type': forms.Select(attrs={ 
                'class': 'block w-full px-4 py-3 text-gray-800 bg-gray-50 border border-gray-300 rounded-xl dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 focus:outline-none transition duration-200 shadow-sm', 
            }),

            # Notes (Textarea) - Wide, rounded, and uses accent focus
            'notes': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 text-gray-800 bg-gray-50 border border-gray-300 rounded-xl dark:placeholder-gray-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 focus:outline-none transition duration-200',
                'rows': 4  # Reduced rows for a cleaner look
            }),
        }


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 ',
            'placeholder': 'Enter your old password',
        }),
        label="Old Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
            'placeholder': 'Enter your new password',
        }),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
            'placeholder': 'Confirm your new password',
        }),
        label="Confirm New Password"
    )

