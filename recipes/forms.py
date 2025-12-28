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

class ReceipeForm(forms.ModelForm):
    class Meta:
        model = Receipe
        fields = ['receipe_name', 'receipe_description', 'receipe_type', 'receipe_image']
        widgets = {
            'receipe_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none placeholder-gray-400',
                'placeholder': 'e.g. Spicy Chicken Curry'
            }),
            'receipe_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none placeholder-gray-400',
                'rows': 4,
                'placeholder': 'Describe the taste, history, or inspiration...'
            }),
            'receipe_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none cursor-pointer'
            }),
            'receipe_image': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-orange-50 file:text-orange-600 hover:file:bg-orange-100 dark:file:bg-orange-900/30 dark:file:text-orange-400 cursor-pointer'
            }),
        }

IngredientFormSet = inlineformset_factory(
    Receipe,
    Ingredients,
    fields=('ingredients_name',),
    widgets={
        'ingredients_name': forms.TextInput(attrs={
            # We style this to look like a clean list item
            'class': 'flex-grow w-full px-4 py-3 rounded-xl bg-stone-50 dark:bg-gray-800 border border-stone-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none',
            'placeholder': 'Enter ingredient (e.g. 2 cups Rice)'
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
            # Recipe Select
            'recipe': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none cursor-pointer shadow-sm'
            }),
            
            # Meal Date (DateInput)
            'meal_date': forms.DateInput(attrs={
                'type': 'date',  
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none cursor-pointer'
            }),
            
            # Meal Time (TimeInput)
            'meal_time': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none cursor-pointer'
            }),
            
            # Meal Type (Select)
            'meal_type': forms.Select(attrs={ 
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none cursor-pointer shadow-sm', 
            }),

            # Notes (Textarea)
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none resize-none placeholder-gray-400',
                'rows': 3,
                'placeholder': 'Add notes (e.g. "Prepare ingredients night before")'
            }),
        }

from django import forms

# Form for the "Forgot Password" page (Email only)
class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none placeholder-gray-400',
            'placeholder': 'Enter your registered email'
        })
    )

# Form for the actual "Change Password" page
class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none placeholder-gray-400',
            'placeholder': 'Enter your old password',
        })
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none placeholder-gray-400',
            'placeholder': 'Enter your new password',
        })
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none placeholder-gray-400',
            'placeholder': 'Confirm your new password',
        })
    )

